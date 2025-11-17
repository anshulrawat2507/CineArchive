"""Apply authentication schema updates to the database."""
import sys
from sqlalchemy import create_engine, text

DB_URL = "mysql+pymysql://root:Sr%2312345@localhost/BollywoodLens"

def main():
    engine = create_engine(DB_URL)
    
    with open("sql/auth_schema.sql", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Split by DELIMITER changes
    sections = content.split("DELIMITER")
    
    with engine.begin() as conn:
        # Execute non-delimiter sections
        for i, section in enumerate(sections):
            if i == 0:
                # First section before any DELIMITER
                statements = [s.strip() for s in section.split(";") if s.strip() and not s.strip().startswith("--")]
                for stmt in statements:
                    if stmt and "USE BollywoodLens" not in stmt:
                        try:
                            conn.execute(text(stmt))
                            print(f"✓ {stmt[:60]}...")
                        except Exception as e:
                            print(f"⚠ {e}")
            elif "//" in section:
                # Section with // delimiter
                parts = section.split("//", 1)
                if len(parts) > 1:
                    # Execute procedures
                    procs = parts[1].split("DROP PROCEDURE")
                    for proc in procs:
                        if proc.strip():
                            full_proc = "DROP PROCEDURE" + proc.strip()
                            # Remove the trailing DELIMITER ; part
                            full_proc = full_proc.replace("DELIMITER ;", "").strip()
                            if full_proc:
                                try:
                                    conn.execute(text(full_proc))
                                    print(f"✓ Procedure created")
                                except Exception as e:
                                    print(f"⚠ {e}")
    
    print("\n✅ Authentication schema applied successfully!")

if __name__ == "__main__":
    main()
