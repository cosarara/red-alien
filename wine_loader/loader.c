
#include <stdlib.h>
#include <string.h>

int main(int argc, char* argv[]) {
  char command[80] = "script.bat ";
  strcat(command, argv[1]);
  strcat(command, " ");
  strcat(command, argv[2]);
  system(command);
  return 0;
}


