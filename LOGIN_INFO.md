# Login Information

## Admin Credentials
- **Username:** `admin`
- **Password:** `1database`

## API Endpoints

### Login
```bash
POST /api/auth/login/
Content-Type: application/json

{
  "username": "admin",
  "password": "1database"
}
```

### Logout
```bash
POST /api/auth/logout/
```

### Health Check
```bash
GET /api/health/
```

## Notes
- The admin user is automatically created on deployment
- All API endpoints allow unauthenticated access for now (configured with AllowAny)
- CORS is enabled for all origins
- Frontend will be built and served from /frontend/build
- Django admin panel available at: `/admin/`
