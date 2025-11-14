# delete_entry.py
from database import ZeroDivisorDatabase

def delete_entry(n):
    """Delete a specific n value from the database"""
    db = ZeroDivisorDatabase()
    
    conn = db._get_connection()
    cursor = conn.cursor()
    
    # First, get the entry_id for this n value
    cursor.execute('SELECT entry_id FROM MyNumber WHERE nvalue = ?', (n,))
    result = cursor.fetchone()
    
    if result:
        entry_id = result[0]
        
        # Delete from ExactConnection table first (foreign key constraint)
        cursor.execute('DELETE FROM ExactConnection WHERE entry_id = ?', (entry_id,))
        
        # Then delete from MyNumber table
        cursor.execute('DELETE FROM MyNumber WHERE nvalue = ?', (n,))
        
        conn.commit()
        conn.close()
        print(f"✓ Successfully deleted Z_{n} from database")
    else:
        print(f"✗ Z_{n} not found in database")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        n = int(sys.argv[1])
        delete_entry(n)
    else:
        print("Usage: python delete_entry.py <n>")