import sqlite3
conn = sqlite3.connect('../data/webui.db')
# conn.execute('''
#              CREATE TABLE IF NOT EXISTS "group" (
#                 id TEXT PRIMARY KEY,
#                 user_id TEXT NOT NULL, 
#                 name TEXT NOT NULL, 
#                 description TEXT NOT NULL,
#                 data JSON, 
#                 meta JSON, 
#                 permissions JSON,
#                 user_ids JSON,
#                 access_control JSON, 
#                 created_at BIGINT NOT NULL, 
#                 updated_at BIGINT NOT NULL)'''
#             )
# conn.execute('''
#              CREATE TABLE IF NOT EXISTS channel (
#                 id TEXT PRIMARY KEY,      
#                 user_id TEXT NOT NULL,                   
#                 type TEXT,                     
#                 name TEXT NOT NULL,                      
#                 description TEXT,                     
#                 data JSON,                              
#                 meta JSON,                         
#                 access_control JSON,                  
#                 created_at BIGINT NOT NULL,          
#                 updated_at BIGINT NOT NULL);'''
#             )
conn.execute('''
            CREATE TABLE IF NOT EXISTS folder (
                id TEXT PRIMARY KEY,                   
                parent_id TEXT,                    
                user_id TEXT NOT NULL,      
                name TEXT NOT NULL,                     
                items JSON,                        
                meta JSON,                         
                is_expanded BOOLEAN NOT NULL DEFAULT 0,
                created_at BIGINT NOT NULL,         
                updated_at BIGINT NOT NULL);'''
             )
conn.commit()
print('Table created')