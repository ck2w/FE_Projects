
df = readtable('Russell_1000_component_stocks.csv', 'ReadVariableNames', false);

results = [];
error_tickers = [];

% tickers = df(1:10, 2);
tickers = df(:, 2);

% download eps data for tickers
for num = 1: size(tickers, 1)
    ticker = tickers{num, 1};
    earnings = scrapeEarningsZacks(ticker);
    if isempty(earnings)
        % no data, drop this ticker (eg: AGO)
        continue;
    end
    has_eps = false;
    disp([num, num/size(tickers,1)]);

    for i = 1:size(earnings, 1)
        if ismember(earnings(i,2), {'Aug 2020', 'Sep 2020', 'Oct 2020'})
            disp(earnings(i,:));
            results = [results; [ticker, earnings(i,:)]];
            has_eps = true;
            break;
        
        end
    end
    if ~has_eps
        earliest_period = datetime(earnings{end, 2}, 'InputFormat', 'MMM yyyy', 'Locale', 'en_US');
        
        if earliest_period > datetime(2020,11,1)
            % new IPO tickers, just drops this ticker (eg: AI)
            continue;
        else
            % no data in Aug/Sep/Oct, might be error
            % the firm just didn't disclose eps data (eg: AXON, AZPN, CRWD, DISCK)
            error_tickers = [error_tickers; ticker];
            continue;
        end
    end
end

used_ticker_nums = size(results, 1);

% convert str to double
for i = 1 : used_ticker_nums
    results{i,2} = replace(results{i,2}, '-20', '-2020');
    results{i,4} = replace(results{i,4}, '$', '');
    results{i,5} = replace(results{i,5}, '$', '');
    results{i,4} = replace(results{i,4}, ' ', '');
    results{i,5} = replace(results{i,5}, ' ', '');
    results{i,4} = str2double(results{i,4});
    results{i,5} = str2double(results{i,5});
    results{i,6} = str2double(results{i,6});
    results{i,7} = str2double(results{i,7});    
end

% sort surprises data in ascending order, get loc(ranking)
surprises = cell2mat(results(:,7));
[~, loc] = sort(surprises);

% sort results based on surprises ranking
sorted_results = results(loc,:);

% drop large surprise
sorted_results = sorted_results((cell2mat(sorted_results(:,7)) < 1000)&(cell2mat(sorted_results(:,7)) > -1000), :);
used_ticker_nums = size(sorted_results, 1);

writecell(sorted_results, 'all_surpries.csv');  
% 
% % split all the stocks into 3 groups
% for i = 1:3
%    group_start = floor(used_ticker_nums * (i-1) / 3) + 1;
%    group_end = floor(used_ticker_nums * i /3);
%    disp([group_start, group_end]);
%    results_group = sorted_results(group_start:group_end, :);
%    if i == 1
%        filename = 'Miss';
%    elseif i==2
%        filename = 'Meet';
%    else
%        filename = 'Beat';
%    end
%    writecell(results_group, [filename, '.csv']);    
% end
% 


