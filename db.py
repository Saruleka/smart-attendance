import sqlite3

conn=sqlite3.connect("student.db")


conn.execute("""
CREATE TABLE IF NOT EXISTS student (
    reg INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    class TEXT NOT NULL
)
""")

conn.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    reg INTEGER,
    class TEXT NOT NULL,
    date TEXT NOT NULL,
    status TEXT CHECK (status IN ('present', 'absent', 'half day')),
    PRIMARY KEY (reg, date),
    FOREIGN KEY (reg) REFERENCES student(reg)
)
""")

conn.commit()

conn.close() 

