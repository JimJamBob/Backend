from rope.base.project import Project
from rope.refactor.move import MoveModule

# Initialize a Rope project in your backend directory
project = Project("path/to/backend")  # Adjust to your backend folder

# Specify the file to move and destination folder
resource = project.get_resource("oauth2.py")  # File to move
destination = project.get_resource("oauth2")  # Target folder

# Create the move refactoring
mover = MoveModule(project, resource)
changes = mover.get_changes(destination)

# Apply the changes
project.do(changes)
print("File moved and imports updated!")