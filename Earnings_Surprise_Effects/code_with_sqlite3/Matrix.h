#pragma once
#ifndef MATRIX_H
#define MATRIX_H

#include <vector>
#include <cmath>
#include <iostream>
#include "Vector.h"
#include "StockData.h"
using namespace std;

class Matrix
{
public:

	
	//setters
	vector<Vector> data;
	Matrix() {};
	Matrix(vector<StockData*> stock_list)
	{
		for (auto iter : stock_list)
		{
			data.push_back(iter->abnormal_return);
		}
	};
	Matrix(vector<Vector> mat_data)
	{
		data = mat_data;
	};
	~Matrix() {};
	void append(Vector& V);

	//getters
	Vector sum();
	Vector mean();
	Vector weighted_mean(Vector weights);
	Vector std();

	

	//operator overloading
	friend ostream& operator << (ostream& out, Matrix & M)
	{
		for (auto itr = M.data.begin(); itr != M.data.end(); itr++)
			out << *itr;
		out << endl;
		return out;
	}

};



#endif
