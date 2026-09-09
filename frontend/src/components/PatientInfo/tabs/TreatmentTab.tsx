import { useCallback, useEffect, useState } from 'react';
import { Pencil, Plus } from 'lucide-react';
import { useWritableFields, invalidateWritableFieldsCache } from '@/hooks/useWritableFields';
import { listTherapyRegimens, type EditableTherapyLine } from '@/api/therapyLines';
import type { TherapyRegimen } from '@/types/therapy';
import ClinicalField from '../ClinicalField';
import Section from '../Section';
import TherapyLineDialog from '../TherapyLineDialog';

interface Props {
  formData: Record<string, unknown>;
  onChange: (field: string, value: unknown) => void;
  diseaseType: 'breast' | 'lymphoma' | 'myeloma' | 'cll' | 'other';
  /** Receives the re-derived record after a line is authored. Without it the tab
   *  still writes correctly but shows stale values until the next refetch. */
  onRecordRefreshed?: (patientInfo: Record<string, unknown>) => void;
}

type TherapyDialogState =
  | { mode: 'add' }
  | { mode: 'edit'; line: EditableTherapyLine };

/**
 * Map the patient's disease string to the Disease vocabulary code for API filtering.
 *
 * Uses the raw disease string (not diseaseType) so MCL and FL are distinguishable —
 * both map to diseaseType='lymphoma' but have different Disease codes.
 * Falls back to the broader diseaseType when the raw string is absent.
 */
function diseaseToDiseaseCode(
  disease: unknown,
  diseaseType: Props['diseaseType'],
): string | undefined {
  // Try the raw disease string first for finer discrimination (MCL vs FL).
  if (typeof disease === 'string') {
    const d = disease.toLowerCase();
    if (d.includes('mantle')) return 'MCL';
    if (d.includes('follicular')) return 'C3209';
    if (d.includes('myeloma') || d === 'mm') return 'C3242';
    if (d.includes('cll') || d.includes('chronic lymphocytic') || d.includes('chronic lymphoid')) return 'C2987';
    if (d.includes('breast')) return 'C9335';
    if (d.includes('diffuse large b-cell') || d.includes('dlbcl')) return 'DLBCL';
  }
  // Fall back to the type-safe diseaseType prop.
  // 'lymphoma' is intentionally omitted — it groups MCL and FL, and picking
  // one code would show the wrong regimens for the other. Without a raw
  // disease string the picker falls back to "search all regimens".
  const TYPE_TO_CODE: Record<string, string> = {
    myeloma: 'C3242',
    cll: 'C2987',
    breast: 'C9335',
  };
  return TYPE_TO_CODE[diseaseType];
}

export default function TreatmentTab({ formData, onChange, diseaseType, onRecordRefreshed }: Props) {
  // person_id rides in the record the tab already receives, so neither the
  // descriptor nor authoring needs an extra prop threaded through both hosts.
  const personId = Number(formData?.person_id ?? formData?.person ?? 0) || null;

  // Ask about *this* patient: whether a field may be edited depends on who is
  // asking and whose record it is, not only on whether the field is mapped.
  const { descriptors } = useWritableFields(personId ?? undefined);
  const [dialogState, setDialogState] = useState<TherapyDialogState | null>(null);

  const field = (label: string, name: string, type: 'text' | 'number' | 'date') => (
    <ClinicalField
      label={label}
      name={name}
      type={type}
      value={formData?.[name]}
      descriptor={descriptors[name]}
      onChange={onChange}
    />
  );

  const linesCount = (() => {
    const v = String(formData?.therapy_lines_count ?? '');
    if (v === '3+') return 3;
    return parseInt(v) || 0;
  })();

  const therapyLines = Array.isArray(formData?.lines_of_therapy)
    ? (formData.lines_of_therapy as EditableTherapyLine[])
    : [];

  // Planned therapy regimen picker: load regimens for the patient's disease + next line.
  const diseaseCode = diseaseToDiseaseCode(formData?.disease, diseaseType);
  const nextLine = linesCount + 1;
  const nextRound = nextLine === 1 ? 'first_line_therapy'
    : nextLine === 2 ? 'second_line_therapy'
    : 'later_line_therapy';
  const [plannedRegimens, setPlannedRegimens] = useState<TherapyRegimen[]>([]);
  const [loadingPlanned, setLoadingPlanned] = useState(false);

  const loadPlannedRegimens = useCallback(async () => {
    if (!diseaseCode) return;
    setLoadingPlanned(true);
    try {
      setPlannedRegimens(await listTherapyRegimens(diseaseCode, nextRound));
    } catch {
      setPlannedRegimens([]);
    } finally {
      setLoadingPlanned(false);
    }
  }, [diseaseCode, nextRound]);

  useEffect(() => {
    (async () => {
      await loadPlannedRegimens();
    })();
  }, [loadPlannedRegimens]);

  return (
    <div>
      {personId !== null && (
        <div className="mb-5 space-y-3">
          <button
            onClick={() => setDialogState({ mode: 'add' })}
            className="inline-flex items-center gap-1.5 rounded-md border border-border px-3 py-1.5 text-sm font-medium hover:bg-muted"
          >
            <Plus size={14} />
            Add therapy line
          </button>
          {therapyLines.length > 0 && (
            <ul className="divide-y divide-border rounded-md border border-border">
              {therapyLines.map((line) => (
                <li
                  key={`${line.episode_id ?? 'no-episode'}-${line.line}`}
                  className="flex items-center gap-3 px-3 py-2 text-sm"
                >
                  <div className="min-w-0 flex-1">
                    <p className="font-medium text-portal-text-primary">
                      Line {line.line}: {line.regimen || 'Unnamed regimen'}
                      {line.intent && (
                        <span className="ml-2 font-normal text-portal-text-secondary">
                          {line.intent}
                        </span>
                      )}
                      {line.outcome && (
                        <span className="ml-2 inline-block rounded bg-muted px-1.5 py-0.5 text-xs font-normal">
                          {line.outcome}
                        </span>
                      )}
                    </p>
                    <p className="truncate text-xs text-portal-text-secondary">
                      {line.start_date || 'No start date'}
                      {line.end_date ? ` to ${line.end_date}` : ' to present'}
                      {line.discontinuation_reason && (
                        <span className="ml-2">Reason: {line.discontinuation_reason}</span>
                      )}
                    </p>
                  </div>
                  <button
                    type="button"
                    disabled={typeof line.episode_id !== 'number'}
                    onClick={() => setDialogState({ mode: 'edit', line })}
                    className="inline-flex items-center gap-1.5 rounded-md border border-border px-2.5 py-1.5 text-xs font-medium hover:bg-muted disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    <Pencil size={13} />
                    Edit
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {dialogState && personId !== null && (
        <TherapyLineDialog
          personId={personId}
          defaultLineNumber={linesCount + 1}
          line={dialogState.mode === 'edit' ? dialogState.line : undefined}
          diseaseCode={diseaseToDiseaseCode(formData?.disease, diseaseType)}
          onClose={() => setDialogState(null)}
          onAuthored={(info) => {
            invalidateWritableFieldsCache(personId);
            onRecordRefreshed?.(info);
          }}
        />
      )}

      <Section title="Treatment History">
        <div className="grid grid-cols-1 gap-x-8 gap-y-5 sm:grid-cols-2">
          {field('Number of Prior Lines', 'therapy_lines_count', 'number')}
          {field('Relapse Count', 'relapse_count', 'number')}
          <div className="sm:col-span-2">
            {field('Refractory Status', 'refractory_status', 'text')}
          </div>
        </div>
      </Section>

      <Section title="Supportive Therapy">
        <div className="grid grid-cols-1 gap-x-8 gap-y-5 sm:grid-cols-2">
          {field('Supportive Therapy Start Date', 'supportive_therapy_start_date', 'date')}
          {field('Supportive Therapy End Date', 'supportive_therapy_end_date', 'date')}
          {field('Supportive Therapies', 'supportive_therapies', 'text')}
          {field('Supportive Therapy Intent', 'supportive_therapy_intent', 'text')}
        </div>
      </Section>

      <Section title="Planned Therapies">
        <div className="grid grid-cols-1 gap-x-8 gap-y-5 sm:grid-cols-2">
          <div className="sm:col-span-2">
            {plannedRegimens.length > 0 ? (
              <div>
                <label
                  htmlFor="planned_therapies"
                  className="block text-sm font-medium text-portal-text-primary mb-1"
                >
                  Planned Therapies
                </label>
                <select
                  id="planned_therapies"
                  value={String(formData?.planned_therapies ?? '')}
                  onChange={(e) => onChange('planned_therapies', e.target.value || null)}
                  className="w-full rounded-md border border-input px-2 py-1.5 text-sm"
                >
                  <option value="">Select a regimen…</option>
                  {plannedRegimens.map((r) => (
                    <option key={r.code} value={r.title}>{r.title}</option>
                  ))}
                </select>
              </div>
            ) : loadingPlanned ? (
              <div>
                <label className="block text-sm font-medium text-portal-text-primary mb-1">
                  Planned Therapies
                </label>
                <p className="text-xs text-muted-foreground">Loading regimens…</p>
              </div>
            ) : (
              field('Planned Therapies', 'planned_therapies', 'text')
            )}
          </div>
        </div>
      </Section>
    </div>
  );
}
