#!/bin/bash

# PostgreSQL Database Fix for Windows
echo "🔧 Fixing PostgreSQL connection issues on Windows..."

# Option 1: Try installing a pre-compiled wheel
echo "📦 Attempting to install pre-compiled psycopg2..."
pip install --upgrade pip
pip install --find-links https://download.lfd.uci.edu/pythonlibs/archived/ psycopg2-binary

# If that fails, try alternative approaches
if [ $? -ne 0 ]; then
    echo "⚠️ Pre-compiled wheel failed, trying alternatives..."
    
    # Option 2: Try psycopg (modern replacement)
    echo "📦 Installing psycopg (modern alternative)..."
    pip install psycopg[binary]
    
    if [ $? -eq 0 ]; then
        echo "✅ psycopg installed successfully!"
        echo "📝 Updating database models to use psycopg..."
        
        # Update the database URL in db_init.py
        cd swifttrack/database
        
        # Create a backup
        cp db_init.py db_init.py.backup
        
        # Update to use psycopg instead of psycopg2
        sed -i 's/postgresql+psycopg2:/postgresql+psycopg:/' db_init.py
        
        echo "🔄 Updated database configuration"
        
    else
        echo "❌ psycopg installation failed"
        
        # Option 3: Use SQLite as fallback
        echo "🔄 Setting up SQLite as fallback database..."
        
        cat > db_init_sqlite.py << 'EOF'
from sqlalchemy import create_engine
from models import Base

# Use SQLite instead of PostgreSQL for development
DATABASE_URL = 'sqlite:///swifttrack.db'

def init_db():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    print("✅ SQLite database initialized successfully!")

if __name__ == '__main__':
    init_db()
EOF
        
        echo "📝 Created SQLite fallback database configuration"
        echo "🚀 Run with: python db_init_sqlite.py"
    fi
fi

echo ""
echo "🎯 Next steps:"
echo "1. Try running: python db_init.py"
echo "2. If that fails, try: python db_init_sqlite.py"
echo "3. Then restart the application: cd ../.. && ./start.sh"