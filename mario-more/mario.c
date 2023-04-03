#include <cs50.h>
#include <stdio.h>

int main(void)
{
    //Get height

    int height;
    do
    {
        height = get_int("Height: ");
    }
    //Repeat while unvalid
    while ((height < 1) || (height > 8));




    //Create pyramids

    //Create Spaces
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < height - i - 1; j++)
        {
            printf(" ");
        }
        //Create Left Bricks
        for (int j = 0; j < i + 1; j++)
        {
            printf("#");
        }

        //Create Gap
        printf("  ");

        //Create Right Bricks
        for (int j = 0; j < i + 1; j++)
        {
            printf("#");
        }


        printf("\n");
    }


}