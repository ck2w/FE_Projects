#include <iostream>
#include "Vector.h"
using namespace std;

int Vector::size() const
{
	return data.size();
}

void Vector::push_back(const double& val)
{
	data.push_back(val);
}

double Vector::back() const
{
	return data.back();
}

Vector Vector::pct_change() const
{
	Vector pct_change;
	pct_change.push_back(0);
	for (unsigned int i = 1; i < data.size(); i++)
	{
		pct_change.push_back(data[i] / data[i - 1]-1);
	}
	return pct_change;
}

double Vector::sum() const
{
	double sum = 0;
	for (auto iter = data.begin(); iter != data.end(); iter++)
	{
		sum += *iter;
	}
	return sum;
}

Vector Vector::cumsum() const
{
	Vector cumsum;
	cumsum.push_back(data[0]);
	for (unsigned int i = 1; i < data.size(); i++)
	{
		cumsum.push_back(cumsum[i - 1] + data[i]);
	}
	return cumsum;
}



void Vector::clear()
{
	vector <double>().swap(data);
}
