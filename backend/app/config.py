import os
from dotenv import load_dotenv

load_dotenv()

# Database: cloud DATABASE_URL if set, else local Docker default.
DB_URL = os.getenv("DATABASE_URL", "postgresql://revision:revision@localhost:5432/revision")

# Frontend origin allowed by CORS: cloud URL if set, else local Vite.
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")