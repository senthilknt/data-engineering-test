import sys

#-------------------------------------------------------------------------------------------------------------------------------
def main():

    """ Format specific tsv file

	Command line args : <input file name> <output file name>
	
    Input tsv file is expected to contain 5 fields per record: id    first_name    last_name    account_number    email
    Supports unlimited number of tabs and line breaks within a record and has logic to piece the record together. 

	Assumptions:
		Two separate records will always be separated by a line break but line breaks can appear within a record
		Two separate fields will always be separated by a tab but tabs can appear within a field
		ID field will always be numeric and will appear in contiguous ascending order. This assumption enables us to have unlimited
		  number of tabs and line breaks within a record. If this assumption is not valid, comment out line 36. This will result in some
		  loss of flexibilty with regards to the number of tabs and line breaks a record can have.

    For better usability, 
		 Tabs and line breaks within id, account_number and email fields are ignored
		 Tabs and line breaks in first_name and last_name fields are preserved
		 account_number field will be cleansed of some characters like /-.
    """

    if len(sys.argv) != 3:
        print('Usage: python cleanse_tsv.py <input file name> <output file name>')
        exit(1)

    inp_name = sys.argv[1]
    outp_name = sys.argv[2]
    
    header,partial,buffer = True,True,[]

    with open(inp_name,encoding='utf-16le') as infile:
    
        with open(outp_name,'w',encoding='utf-8') as outfile:

		    outfile.write(infile.readline())  # copy header line
            
            for inrec in infile:
                inlist = inrec.split('\t')
                if not partial: 
                # logic detect start of new record
                    if (is_number(inlist[0]) 
                        and not is_number(buffer[-1]) 
                        and (int(inlist[0]) - 1) == int(buffer[0])): 
                        write_out(outfile,buffer)
                        buffer = inlist
                    else:
                        merge_record(buffer,inlist)
                else:
                    merge_record(buffer,inlist)
                    
                if len(buffer) >= 5:
                    partial = False
                else:
                    partial = True
            
            write_out(outfile,buffer) # write last line

#-------------------------------------------------------------------------------------------------------------------------------
def merge_record(buffer,new):

    # logic to merge multiple lines when they are part of the same record
	
    buffer_len = len(buffer)
    field_count = len(new)
    
    if buffer_len == 0:
        buffer.append(new[0])
    else:
        if buffer[-1] == '\n': #line break between fields - do not treat line break as a separate field 
            buffer[-1] = new[0]
        elif is_number(buffer[-1].replace("\n","")) and is_number(new[0]): #ignore embedded line breaks in numeric fields
            buffer[-1] = str(buffer[-1]).replace('\n','') + str(new[0])
        else: # add quote around fields with embedded line breaks
            buffer[-1] = '"' + str(buffer[-1]).replace('"','') + str(new[0]) + '"'

    for i in range(1,len(new)):
        buffer.append(new[i])
#-------------------------------------------------------------------------------------------------------------------------------
def write_out(file,list):
    
    # rationailse output record
        # ignore embedded tabs and line breaks within numeric and email fields
        # try to clean up account number field
        # handle extra tabs in the record 

    temp =[]
    for field in list:  # remove tabs from numeric fields
        if len(temp) > 0 and is_number(temp[-1]) and is_number(field):
            temp[-1] = temp[-1] + field
        else:
            temp.append(field)

    account,email,email2,out = False,False,False,[]

    for i in range(0,len(temp)): # rationalise record based on the expected layout (id,first_name,last_name,account_number,email)
        field = temp[i]
        if i > 2 and is_number(field):
            account = True

        if i > 2 and account and not is_number(field):
            email = True
            account = False
        
        if i > 2 and not account and not email:
            out[-1] = '"' + str(out[-1]).replace('"','') + '\t' + str(field).replace('"','') + '"'
        elif account:
            out.append(field.replace("-","").replace("/","").replace(".","").replace("_","").replace('"','').replace("\n",""))
        elif email and not email2:
            email2 = True
            out.append(field.replace("\n",""))
        elif email2:
            out[-1] = out[-1] + field.replace("\n","").replace('"',"")
        else:
            out.append(field)
    
    if len(out) != 5: # rationalisation did not work due to unexpected data. Switch to default splitting logic
        out = []
        for i in range(0,len(temp)):
            if i > 4:
                out[-1] = '"' + str(out[-1]).replace('"','') + '\t' + str(temp[i]).replace('"','') + '"'
            else:
                out.append(temp[i])
    
    # write to output file making sure line break is added    
    rec = '\t'.join(map(str, out))        
    if rec[-1] != '\n':
        file.write(rec +'\n')
    else:
        file.write(rec)
        
#-------------------------------------------------------------------------------------------------------------------------------
def is_number(s):
    try:
        float(s.replace("\n","").replace("/","").replace("-","").replace('"',""))
        return True
    except ValueError:
        return False
#-------------------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    main()

