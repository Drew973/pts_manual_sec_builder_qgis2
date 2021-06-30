from zipfile import ZipFile
import os



#copys everything except .git ,__pycache__ folders and .pyc extention in folder to zip file zip_name


#need filenames 1st otherwise looping through zip?
def package(folder,zip_name=None,exclude_ext=['.pyc','.zip']):

    if not zip_name:
        zip_name =os.path.basename(folder)+'.zip'
        print(zip_name)


    files=[]

    # create a ZipFile object
       # Iterate over all the files in directory
    for folderName, subfolders, filenames in os.walk(folder):
        if not '.git' in folderName and not '__pycache__' in folderName:
               
            for filename in filenames:
                filePath = os.path.join(folderName, filename)
                if not os.path.splitext(filePath)[1] in exclude_ext:
                    #zipObj.write(filePath, basename(filePath))
                    files.append(os.path.relpath(filePath,folder))
    
    
    
    folder_name = os.path.splitext(zip_name)[0]
    print(folder_name)
    
    with ZipFile(zip_name, 'w') as z:
        for f in files:
            z.write(f,os.path.join(folder_name,f))
            print(f)



if __name__ == "__main__":
    package(os.getcwd())


