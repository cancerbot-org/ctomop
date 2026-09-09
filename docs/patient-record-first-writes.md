# PatientRecord-First Write Architecture

## Problem

The original write architecture had two frontend paths:

1. **OMOP-mapped fields** (hemoglobin, ANC, etc.) wrote to OMOP clinical endpoints
   (`POST /v1/measurements/`, `POST /v1/observations/`), then relied on `post_save`
   signals to re-derive `PatientRecord`.

2. **Unmapped fields** (planned_therapies, etc.) wrote directly to `PatientRecord` via PATCH.

This created several problems:

- **Split brain**: the frontend needed to classify every field and route it to the
  right endpoint, duplicating backend logic.
- **User edits lost on derivation**: when derivation re-ran (triggered by any OMOP
  write), it overwrote PatientRecord from OMOP tables — wiping any value that wasn't
  yet backed by an OMOP fact.
- **Mapping-approval disconnect**: approving a `FieldConceptMapping` didn't
  retroactively project existing user edits into OMOP, leaving a gap.
- **Fragile save path**: the frontend had to fetch the writable-field descriptor,
  split edits by target, write OMOP facts individually (with supersede logic), then
  PATCH only the remaining fields — and an error in any step could leave the save
  half-done.

## Solution

**All UI edits write to PatientRecord first.** The backend handles OMOP projection
as a side-effect for fields with approved mappings.

### Write flow

```
User edits a field
    |
    v
Frontend: PATCH /api/patient-info/{person_id}/
    |  (all writable fields in one request, except Person profile fields)
    v
Backend: PatientRecordSerializer.save()
    |  (value lands on PatientRecord immediately)
    |
    +---> user_edited_fields tracking (for derivation preservation)
    |
    +---> _project_mapped_fields()
    |       |
    |       +---> For each patched field with an approved FieldConceptMapping:
    |       |       project_single_value() upserts the OMOP fact
    |       |
    |       +---> refresh_patient_record() once at the end
    |
    v
Response to frontend
```

### Profile fields

Fields targeting `Person` (gender, race, ethnicity, address) still go to the
persons endpoint (`PATCH /v1/persons/{id}/`) because they are a different resource.
The frontend sends them via `writeProfileFields()`.

## Write Descriptor Changes

The `build_writable_field_descriptor()` function now returns `KIND_DIRECT` with
`target: 'patient_record'` for all clinical fields. Fields with approved OMOP
mappings carry a `projection` key:

```python
# Field with an approved mapping (e.g., hemoglobin via LOINC 718-7):
{
    'kind': 'direct',
    'writable': True,
    'target': 'patient_record',
    'value_kind': 'number',
    'unit': 'g/dL',
    'projection': {
        'omop_table': 'measurement',
        'concept_id': 3000963,
        'code': '718-7',
        'vocabulary': 'LOINC',
        'display': 'Hemoglobin',
        'unit': 'g/dL',
        'unit_concept_id': 8713,
        'type_concept_id': 32865,
        'source_value': '718-7',
    },
}

# Field without a mapping (e.g., planned_therapies):
{
    'kind': 'direct',
    'writable': True,
    'target': 'patient_record',
    'value_kind': 'string',
    'reason': 'Written directly to PatientRecord. No OMOP mapping yet.',
}
```

### KIND_EDITABLE is retired

The `KIND_EDITABLE` constant still exists for backward compatibility but is no
longer emitted by the descriptor builder. All writable clinical fields are
`KIND_DIRECT`.

### Vocabulary not loaded

When the vocabulary doesn't carry a concept (e.g., LOINC not loaded), the field is
still `KIND_DIRECT` and writable — the value lands on PatientRecord and is preserved
across derivation. No `projection` key is present, so no OMOP fact is created.

## OMOP Projection

### At PATCH time (`project_single_value`)

When a field is patched and has an approved `FieldConceptMapping`, the backend
calls `project_single_value()` to upsert the OMOP fact:

- Upserts by `(person_id, source_value)` to avoid duplicates.
- Updates the value on an existing fact; creates a new one if none exists.
- Sets `_skip_patient_record_refresh = True` on the OMOP instance to avoid
  recursive derivation.
- One `refresh_patient_record()` call at the end picks up all projected facts.

### At mapping approval (`project_field_to_omop`)

When a curator approves a `FieldConceptMapping`, the `post_save` signal triggers
`project_field_to_omop()`, which backfills all PatientRecords that have a
user-edited value for that field.

## Derivation Preservation

`refresh_patient_record()` snapshots `user_edited_fields` before derivation and
restores values that derivation produced nothing for. Once an OMOP fact exists
(from projection or any other source), derivation wins and the field drops from
`user_edited_fields`.

## Frontend Simplification

### Before (split brain)

```typescript
// Clinical edits → OMOP endpoints
await writeFieldValues(personId, clinicalEdits);
// Direct edits → PatientRecord PATCH
await api.patch(`/patient-info/${personId}/`, directFields);
```

### After (single path)

```typescript
// Profile fields → persons endpoint
await writeProfileFields(personId, profileEdits);
// Everything else → PatientRecord PATCH
await api.patch(`/patient-info/${personId}/`, patchFields);
```

The frontend no longer needs to know which fields are OMOP-mapped. It classifies
fields into two buckets:

1. `target === 'person'` → persons endpoint
2. Everything else → PatientRecord PATCH

## Key Files

| File | Role |
|------|------|
| `omop_core/services/write_descriptor.py` | Builds field descriptors with projection metadata |
| `omop_core/services/omop_projection.py` | `project_single_value()` (PATCH-time) and `project_field_to_omop()` (mapping approval) |
| `patient_portal/api/views.py` | `partial_update()` calls `_project_mapped_fields()` after save |
| `omop_core/services/patient_record_service.py` | Derivation snapshots/restores `user_edited_fields` |
| `omop_core/signals.py` | `post_save` on `FieldConceptMapping` triggers projection |
| `frontend/src/components/Patient/PatientDetail.tsx` | Provider editor doSave |
| `frontend/src/federation/PatientInfo.tsx` | Federation view doSave |
| `frontend/src/hooks/useWritableFields.ts` | FieldDescriptor type with projection |

## Invariants

1. **Every user edit is captured immediately** — the PatientRecord PATCH always
   lands, regardless of mapping state. No edit is lost because a field lacks a
   mapping.

2. **Projection is best-effort** — a projection failure does not roll back the
   PatientRecord write. The value is safely stored and projection can be retried.

3. **Derivation cannot overwrite user edits** — `user_edited_fields` tracking
   ensures user values persist until an OMOP fact backs them.

4. **Mapping approval triggers backfill** — existing user edits are projected
   when a mapping is approved, without any manual step.

5. **The frontend has one write path** — no more split between OMOP and
   PatientRecord. The descriptor still carries projection metadata for the date
   picker UI, but routing is server-side.
