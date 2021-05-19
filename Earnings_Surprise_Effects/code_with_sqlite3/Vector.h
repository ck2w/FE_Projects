
#ifndef Vector_H
#define Vector_H

#include <vector>
#include <cmath>
#include <iostream>
#include <iomanip>

using namespace std;

class Vector
{
public:
	vector<double> data;

	Vector() {};
	Vector(vector<double> data_) :data(data_) {};
	~Vector() {};

	// setters
	void push_back(const double& val);
	void clear();

	// getters
	int size() const;
	double back() const;
	Vector pct_change() const;	
	double sum() const;
	Vector cumsum() const;

	Vector operator-(Vector& a)
	{
		int d = a.size();
		vector<double> V(d);
		for (int i = 0; i < d; i++)
		{
			V[i] = data[i] - a[i];
		};
		return Vector(V);
	};
	Vector operator+(Vector& a)
	{
		int d = a.size();
		vector<double> V(d);
		for (int i = 0; i < d; i++)
		{
			V[i] = data[i] + a[i];
		};
		return Vector(V);
	};

	double operator[](int const idx) const
	{
		return data[idx];
	};
	
	friend ostream& operator<<(ostream& out, Vector& V)
	{
		for (auto itr = V.data.begin(); itr != V.data.end(); itr++)
			out << setw(15) << *itr;
		out << endl;
		return out;
	};

};


#endif 
