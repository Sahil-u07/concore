function [result] = concore_initval(simtime_val)
    global concore;
    % Safe numeric parsing (replaces unsafe eval)
    clean_str = strtrim(simtime_val);
    clean_str = regexprep(clean_str, '[\[\]]', '');
    result = sscanf(clean_str, '%f').';
    concore.simtime = result(1);
    result = result(2:length(result));
end
