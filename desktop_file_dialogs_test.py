################
###  Folder  ###
################

from desktop_file_dialogs import Desktop_FolderDialog, FileGroup
Desktop_FolderDialog(
  title             = "Select Folder",
  initial_directory = "",
  on_accept         = lambda folder_path: print(">>>", folder_path      ),
  on_cancel         = lambda:             print(">>> NO FOLDER SELECTED"),
).show()


##############
###  File  ###
##############

from desktop_file_dialogs import Desktop_FileDialog, FileGroup
Desktop_FileDialog(
  title             = "Select File",
  initial_directory = "",
  on_accept         = lambda file_path: print(">>>", file_path      ),
  on_cancel         = lambda:           print(">>> NO FILE SELECTED"),
  file_groups = [
    FileGroup(name="Image Files", extensions=["jpg", "jpeg", "png", "gif"]),
    FileGroup.All_FileTypes,
  ],
).show()


###############
###  Files  ###
###############

from desktop_file_dialogs import Desktop_FilesDialog, FileGroup
Desktop_FilesDialog(
  title             = "Select Files",
  initial_directory = "",
  on_accept         = lambda file_paths: print(">>>", file_paths      ),
  on_cancel         = lambda:            print(">>> NO FILES SELECTED"),
  file_groups = [
    FileGroup(name="Image Files", extensions=["jpg", "jpeg", "png", "gif"]),
    FileGroup.All_FileTypes,
  ],
).show()


##################
###  SaveFile  ###
##################

from desktop_file_dialogs import Desktop_SaveFile_Dialog, FileGroup
Desktop_SaveFile_Dialog(
  title             = "Save As",
  initial_directory = "",
  on_accept         = lambda file_path: print(">>>", file_path         ),
  on_cancel         = lambda:           print(">>> FILE SAVE CANCELLED"),
  file_groups = [
    FileGroup(name="JPEG", extensions=["jpg", "jpeg"]),
    FileGroup(name="PNG",  extensions=["png"        ]),
    FileGroup.All_FileTypes,
  ],
).show()
