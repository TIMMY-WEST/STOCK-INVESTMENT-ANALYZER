import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

def execute_sql_file(file_path):
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        
        cursor = conn.cursor()
        
        # SQLファイルを読み込み
        with open(file_path, 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        # SQLを実行
        cursor.execute(sql_content)
        conn.commit()
        
        print(f'SQLファイル {file_path} の実行が完了しました。')
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f'エラー: {e}')

if __name__ == "__main__":
    execute_sql_file('scripts/create_timeframe_indexes.sql')