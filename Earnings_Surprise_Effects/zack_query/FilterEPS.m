
sorted_results = table2cell(readtable('all_surpries.csv', 'ReadVariableNames', false));


% drop large surprise
sorted_results = sorted_results((cell2mat(sorted_results(:,7)) < 1000)&(cell2mat(sorted_results(:,7)) > -1000), :);

used_ticker_nums = size(sorted_results, 1);

formatOut = 'yyyy-mm-dd';
for i = 1 : used_ticker_nums

    sorted_results{i,2} = datestr(sorted_results{i,2}, formatOut);
end

% writecell(sorted_results, 'all_surpries2.csv');  

% split all the stocks into 3 groups
for i = 1:3
   group_start = floor(used_ticker_nums * (i-1) / 3) + 1;
   group_end = floor(used_ticker_nums * i /3);
   disp([group_start, group_end]);
   results_group = sorted_results(group_start:group_end, :);
   if i == 1
       filename = 'Miss';
   elseif i==2
       filename = 'Meet';
   else
       filename = 'Beat';
   end
   writecell(results_group, [filename, '.csv']);    
end
