import shutil
import datetime

# function to backup database site.db
def backup_database():
    current_time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_file = f"backup-{current_time}.db"
    shutil.copyfile('site.db', backup_file)  
    
if __name__ == "__main__":
    backup_database()
