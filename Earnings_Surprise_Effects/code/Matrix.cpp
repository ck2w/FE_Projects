#include <iostream>
#include "Matrix.h"
using namespace std;

void Matrix::append(Vector& V)
{
	data.push_back(V);
}

Vector Matrix::sum()
{
	vector<double> sumvec;
	
	for ( int i = 0; i < data[0].size(); i++)
	{
		double columnsum = 0;
		for ( int j = 0; j < data.size(); j++)
		{
			columnsum = columnsum + data[j][i];
		}
		sumvec.push_back(columnsum);
	}
	return Vector(sumvec);

}

Vector Matrix::mean()
{
	vector<double> meanvec;
	
	for ( int i = 0; i < data[0].size(); i++)
	{
		double columnsum = 0;
		for ( int j = 0; j < data.size(); j++)
		{
			columnsum = columnsum + data[j][i];
		}
		meanvec.push_back(columnsum / data.size());
	}
	return Vector(meanvec);
}

Vector Matrix::weighted_mean(Vector weights)
{
	vector<double> meanvec;
	double weights_sum = weights.sum();

	for (int i = 0; i < data[0].size(); i++)
	{
		double columnsum = 0;
		for (int j = 0; j < data.size(); j++)
		{
			columnsum = columnsum + data[j][i] * weights[j];
		}
		meanvec.push_back(columnsum / weights_sum);
	}
	return Vector(meanvec);
}

Vector Matrix::std()
{
	vector<double> stdvec;
	vector<double> meanvec;

	for ( int i = 0; i < data[0].size(); i++)
	{
		double columnsum = 0;
		for ( int j = 0; j < data.size(); j++)
		{
			columnsum = columnsum + data[j][i];
		}
		meanvec.push_back(columnsum / data.size());
	}
	for ( int i = 0; i < data[0].size(); i++)
	{
		double sumsquare = 0;
		for ( int j = 0; j < data.size(); j++)
		{
			double num = data[j][i] - meanvec[i];
			sumsquare += pow(num, 2);
		}
		stdvec.push_back(sqrt(sumsquare / data.size()));
	}
	
	return Vector(stdvec);
}

