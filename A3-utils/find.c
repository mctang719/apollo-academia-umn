#include <stdio.h>
#include <string.h>
#include <dirent.h>
#include <sys/stat.h>


//do we have to deal with symbolic links

void find(char* startingDir, char* filename);

int main(int argc, char** argv)
{
    if (argc != 3)
    {
        fprintf(stderr, "Usage: %s <filename> <starting directory>\n", argv[0]);
	    return 1;
    }
    
    find(argv[2], argv[1]);

    return 0;
}

void find(char* dirName, char* filename)
{
    DIR *dir; //starting directory
    
    char fname[256]; //holds the filename
    int fname_len = strlen(dirName);
    strcpy(fname, dirName); //copy the directory name for modification
    fname[fname_len++] = '/';
    
    if(fname_len > 256)
    {
        printf("Name too long \n.");
        return;
    }
    
    if(!( dir = opendir(dirName)))
    {
        fprintf(stderr, "Can't open dir %s or not found\n.", dirName);
        return;
    }
    
    struct stat s;
    struct dirent *current;
    
    while( (current = readdir(dir)))
    {
        
        if (!current->d_name[0] == '.')
			continue; //prevent traversing infinitely
		if (!strcmp(current->d_name, ".") || !strcmp(current->d_name, ".."))
			continue; //prevent traversing infinitely
        
        // printf("Current item : %s\n", current->d_name);
    
        strncpy(fname + fname_len, current->d_name, 256 - fname_len);
        //using d_type and macros work on Linux and BSD systems, avoids need to use lstat
        
        if(stat(fname, &s) == -1 )
            fprintf(stderr, "Cannot stat %s\n.", fname);
        
        if(S_ISDIR(s.st_mode))
        {
            // printf("Directory: %s\n", current->d_name);
            find(fname, filename);
        }
        else if(strcmp(current->d_name,filename) == 0)
        {
            printf("Found file match %s.\nLocation: %s\n", filename, fname);
        }
    }
    if(dir)
        closedir(dir);
}