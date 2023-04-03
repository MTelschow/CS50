#include <cs50.h>
#include <stdio.h>

int main(void)
{
    bool check(long number);
    long last_digit(long number);
    bool is_digit(long n);
    long rm_end(long number);
    long get_length(long number);
    int leading_digits(long number);
    int sort(long number);


    //Get user Input
    long number;
    do
    {
        number = get_long("Number: ");
    }
    //Validate the input
    while (number < 0);

    //Get the correct answer
    int answer = sort(number);

    //Print the correct text
    if (answer == 0)
    {
        printf("INVALID\n");
    }
    else if (answer == 1)
    {
        printf("AMEX\n");
    }
    else if (answer == 2)
    {
        printf("MASTERCARD\n");
    }
    else
    {
        printf("VISA\n");
    }






}


//Return the last digit
long last_digit(long number)
{
    return number % 10;
}

//Check if it is a single digit number
bool is_digit(long n)
{
    return n == last_digit(n);
}

//Remove the last digit
long rm_end(long number)
{
    return (number - last_digit(number)) / 10;
}

//Returns the length of the number
long get_length(long number)
{
    long i = 0;
    while (number > 0)
    {
        number = rm_end(number);
        i++;
    }
    return i;
}

//Checks the validity of the number
bool check(long number)
{
    //End sum
    int result = 0;
    //Sum of all other digits*2 digits
    int sum = 0;
    while (number > 0)
    {
        //Add digit to sum
        result += last_digit(number);
        number = rm_end(number);

        //Double other digit
        int temp = last_digit(number) * 2;
        //While digit add
        if (is_digit(temp))
        {
            sum += temp;
        }
        //Else add both digits of temp
        else
        {
            sum += last_digit(temp);
            temp = rm_end(temp);
            sum += last_digit(temp);
        }

        number = rm_end(number);
    }

    result += sum;
    return (result % 10) == 0;

}

//Returns the two leading digits
int leading_digits(long number)
{
    while (get_length(number) > 2)
    {
        number = rm_end(number);
    }
    return number;
}



// Returns the creditcard provider
int sort(long number)
{
    if (check(number))
    {
        if (get_length(number) == 15 && (leading_digits(number) == 34 || leading_digits(number) == 37))
        {
            return 1;
        }


        else if (get_length(number) == 16 && (leading_digits(number) > 50 && leading_digits(number) < 56))
        {
            return 2;
        }


        else if ((get_length(number) == 13 || get_length(number) == 16) && (leading_digits(number) >= 40 && leading_digits(number) <= 49))
        {
            return 3;
        }



    }
    return 0;
}