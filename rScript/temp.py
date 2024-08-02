import subprocess
import os
import sys

if len(sys.argv) < 2:
    print("No session folder path provided.")
    sys.exit(1)

session_folder = sys.argv[1]
print(session_folder)
# Path to your R script
r_script_path = 'Analysis2.R'

os.chdir('D:/Raylab/NewNetwork/rScript')

env = os.environ.copy()
env['SESSION_FOLDER'] = session_folder

# Run the R script using subprocess
result = subprocess.run(['C:/Program Files/R/R-4.2.1/bin/Rscript', r_script_path,session_folder], capture_output=True, text=True,  env=env)

# if result.returncode != 0:
#     print(f"R script failed with return code {result.returncode}")
#     print(f"Error output:\n{result.stderr}")
# else:
#     print("R script ran successfully.")
#     print(f"Output:\n{result.stdout}")

if result.returncode != 0:
    # Print error message to be captured by parent script
    print(f"Error: R script failed with return code {result.returncode}\n{result.stderr}")
    sys.exit(result.returncode)
else:
    # Print successful message to be captured by parent script
    print(f"Output:\n{result.stdout}")
    sys.exit(0)