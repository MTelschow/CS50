#include "helpers.h"
#include <math.h>

// Convert image to grayscale
void grayscale(int height, int width, RGBTRIPLE image[height][width])
{
    //For each pixel
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            //Get value
            BYTE new_value = (image[i][j].rgbtBlue + image[i][j].rgbtGreen + image[i][j].rgbtRed) / 3;

            if ((image[i][j].rgbtBlue + image[i][j].rgbtGreen + image[i][j].rgbtRed) % 3 == 2)
            {
                new_value++;
            }

            //Set new values
            image[i][j].rgbtBlue = new_value;
            image[i][j].rgbtGreen = new_value;
            image[i][j].rgbtRed = new_value;
        }
    }
    return;
}


// Reflect image horizontally
void reflect(int height, int width, RGBTRIPLE image[height][width])
{
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            int k = width - j - 1;

            if (j < k)
            {
                BYTE tempBlue = image[i][j].rgbtBlue;
                BYTE tempGreen = image[i][j].rgbtGreen;
                BYTE tempRed = image[i][j].rgbtRed;

                image[i][j].rgbtBlue = image[i][k].rgbtBlue;
                image[i][j].rgbtGreen = image[i][k].rgbtGreen;
                image[i][j].rgbtRed = image[i][k].rgbtRed;

                image[i][k].rgbtBlue = tempBlue;
                image[i][k].rgbtGreen = tempGreen;
                image[i][k].rgbtRed = tempRed;
            }
        }
    }
    return;
}



// Blur image
void blur(int height, int width, RGBTRIPLE image[height][width])
{
    RGBTRIPLE blured[height][width];

    //For each pixel
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            //Set a count of compare pixels
            int count = 0;
            float totalBlue = 0;
            float totalGreen = 0;
            float totalRed = 0;

            //For every pixel in a 3x3 grid
            for (int k = 0; k < 3; k++)
            {
                for (int l = 0; l < 3; l++)
                {
                    if ((i + k - 1) >= 0 && (i + k - 1) < height && (j + l - 1) >= 0 && (j + l - 1) < width)
                    {
                        //Add up all color values
                        totalBlue += image[i + k - 1][j + l - 1].rgbtBlue;
                        totalGreen += image[i + k - 1][j + l - 1].rgbtGreen;
                        totalRed += image[i + k - 1][j + l - 1].rgbtRed;
                        //Increase count
                        count++;
                    }
                }

            }
            blured[i][j].rgbtBlue = (BYTE) round(totalBlue / count);
            blured[i][j].rgbtGreen = (BYTE) round(totalGreen / count);
            blured[i][j].rgbtRed = (BYTE) round(totalRed / count);
        }
    }

    //Add new values from the blured array to the image array
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            image[i][j].rgbtBlue = blured[i][j].rgbtBlue;
            image[i][j].rgbtGreen = blured[i][j].rgbtGreen;
            image[i][j].rgbtRed = blured[i][j].rgbtRed;
        }
    }
    return;
}







// Detect edges
void edges(int height, int width, RGBTRIPLE image[height][width])
{
    //Create a array for storing the new values
    RGBTRIPLE edged[height][width];

    //Gx matrix
    int gx[3][3] =
    {
        {-1, 0, 1},
        {-2, 0, 2},
        {-1, 0, 1}
    };
    //Gy matrix
    int gy[3][3] =
    {
        {-1, -2, -1},
        {0, 0, 0},
        {1, 2, 1}
    };


    //For each pixel
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            //Make variables for every gx & gy value
            float gxBlue = 0;
            float gyBlue = 0;
            float gxGreen = 0;
            float gyGreen = 0;
            float gxRed = 0;
            float gyRed = 0;

            //Calculate for each pixel in 3x3 area
            for (int k = 0; k < 3; k++)
            {
                for (int l = 0; l < 3; l++)
                {
                    if (((i + k - 1) >= 0 && (i + k - 1) < height && (j + l - 1) >= 0 && (j + l - 1) < width))
                    {
                        gxBlue += image[i + k - 1][j + l - 1].rgbtBlue * gx[k][l];
                        gyBlue += image[i + k - 1][j + l - 1].rgbtBlue * gy[k][l];
                        gxGreen += image[i + k - 1][j + l - 1].rgbtGreen * gx[k][l];
                        gyGreen += image[i + k - 1][j + l - 1].rgbtGreen * gy[k][l];
                        gxRed += image[i + k - 1][j + l - 1].rgbtRed * gx[k][l];
                        gyRed += image[i + k - 1][j + l - 1].rgbtRed * gy[k][l];
                    }
                }
            }


            //Calculate color value and cap it at 255
            if (round(sqrt((gxBlue * gxBlue) + (gyBlue * gyBlue))) <= 255)
            {
                edged[i][j].rgbtBlue = (BYTE) round(sqrt((gxBlue * gxBlue) + (gyBlue * gyBlue)));
            }
            else
            {
                edged[i][j].rgbtBlue = (BYTE) 255;
            }

            if (round(sqrt((gxGreen * gxGreen) + (gyGreen * gyGreen))) <= 255)
            {
                edged[i][j].rgbtGreen = (BYTE) round(sqrt((gxGreen * gxGreen) + (gyGreen * gyGreen)));
            }
            else
            {
                edged[i][j].rgbtGreen = (BYTE) 255;
            }

            if (round(sqrt((gxRed * gxRed) + (gyRed * gyRed))) <= 255)
            {
                edged[i][j].rgbtRed = (BYTE) round(sqrt((gxRed * gxRed) + (gyRed * gyRed)));
            }
            else
            {
                edged[i][j].rgbtRed = (BYTE) 255;
            }
        }
    }


    //Add new values from the edges array to the image array
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            image[i][j].rgbtBlue = edged[i][j].rgbtBlue;
            image[i][j].rgbtGreen = edged[i][j].rgbtGreen;
            image[i][j].rgbtRed = edged[i][j].rgbtRed;
        }
    }

    return;
}