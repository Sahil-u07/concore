function concore_default_maxtime(default)
    global concore; 
    try
        maxfile = fopen(strcat(concore.inpath,'1/concore.maxtime'));
        instr = fscanf(maxfile,'%c');
        % Safe numeric parsing (replaces unsafe eval)
        clean_str = strtrim(instr);
        clean_str = regexprep(clean_str, '[\[\]]', '');
        concore.maxtime = sscanf(clean_str, '%f');
        fclose(maxfile);
    catch exc 
        concore.maxtime = default;
    end
end

