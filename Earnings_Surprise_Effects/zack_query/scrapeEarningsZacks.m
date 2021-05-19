% https://www.mathworks.com/matlabcentral/fileexchange/42319-historical-earnings-data-by-ticker-symbol
function [ earnings ] = scrapeEarningsZacks( Stock )
%called by get_hist_earnings
% output format:
%    earnings, a cell array of the data.  
%  Headers are: date, period end, estimate, reported, surprise, surprise % 
%  parses up the earnings table from Zacks.thestreet.com into usable parts
s=urlread('http://zacks.thestreet.com/CompanyView.php','post',{'ticker',Stock});
try etst=strfind(s,'Surprise%</strong></div></td>');
catch 
    fprintf('Error: No earnings data available for %s',Stock)
    earnings={};
    return
end
etend=strfind(s(etst:end),' </table>');
et=s(etst:etst+etend);
rowend=strfind(et,'</tr>');
earnings=cell(length(rowend)-2,6);
% Look for the earnings numbers and dates within the table
for i = 1:(length(rowend)-1) %first one ends header row
    if i==length(rowend)
        row=et(rowend(i):end);
    else
    row=et(rowend(i):rowend(i+1));
    end
    dst=strfind(row,'<td>');
    for j=1:6 %six items in each row
        if j==6
            a=row(dst(j):end-23);
        else
            a=row(dst(j):dst(j+1));
        end
        earnings{i,j}=a(5:(end-38));
    end % for j=
end % for i=
% remove empty rows
emptyCells = cellfun(@isempty,earnings);
[row,~]=find(emptyCells);
earnings(row,:)=[];

end %function

