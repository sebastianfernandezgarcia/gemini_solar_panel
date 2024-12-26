import os
import shutil

damaged_folder = 'Placas dañadas'
undamaged_folder = 'Placas no dañadas'
test_folder = 'test'

if not os.path.exists(test_folder):
    os.makedirs(test_folder)

for filename in os.listdir(damaged_folder):
    new_filename = f"{os.path.splitext(filename)[0]}_D{os.path.splitext(filename)[1]}"
    shutil.move(os.path.join(damaged_folder, filename), os.path.join(test_folder, new_filename))

for filename in os.listdir(undamaged_folder):
    shutil.move(os.path.join(undamaged_folder, filename), os.path.join(test_folder, filename))

print("Files have been successfully moved and renamed.")