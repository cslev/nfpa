package.path = package.path ..";?.lua;test/?.lua;app/?.lua;"


require "Pktgen";



-- ################### CONFIGURATION PART ########################

-- for config params read from the config file

-- local variables for config parameters (read from config.cfg)
config = {};



-- +++++++++++++++++++++++++ FUNCTION ++++++++++++++++++++++++++++
function read_config_file ()

  print("Reading the config file... (nfpa.cfg)\n");

  -- Opens a file in read
  config_file = io.open("nfpa.cfg", "r");

  -- sets the default input file as test.lua
  io.input(config_file);

  print("Read config params:\n");
  -- loop over all lines in the config file
  for line in io.lines()
  do
    -- omit commented lines (check the first letter whether it is '#')
    -- and also omit empty lines
    if not (string.sub(line,0,1)=="#") and (line ~= "")
    then
      -- tokenize and put the config params into a dictionary
      -- first, find equal sign position
      -- string.find only matches the first equal sign, so we do not need
      -- to worry about it and/or escaping further equal signs as special chars
      local equal_pos = string.find(line,"=");
      -- accordingly, key will be the substring before equal sign
      key = string.sub(line,0,equal_pos-1);
      -- and value will be the substring after equal sign
      value = string.sub(line,equal_pos+1);
        -- store other config parameters in config var
        -- such as measureDuration, sendPort, recvPort, etc.
        config[key] = value;
        if key == "biDir"
        then
          print(key,"\t\t",value);
        else
          print(key,"\t",value);
        end
      
    else
     -- nothing to do, these lines are comments <-- Lua has no continue
     -- statement. That's why this check is done likewise
    end
  end

  -- closes the opened file
  io.close(config_file);
  
end
-- ====================== END FUNCTION ========================

function parse_config ()
  -- determine port rate
  print("Parsing configuration file...");  
  
  -- check for special ul-dl birdirectional traffic
  for key,value in pairs(config)
  do
    if key == "trafficType"
    then
      pipe_sign = string.find(value,"|");
      if pipe_sign ~= nil
      then
        t1 = string.sub(value,0,pipe_sign-1);
        t2 = string.sub(value,pipe_sign+1);
        print("2 traffic files for the two ports: " .. t1 .. " and " .. t2 ..
              "\n");
        -- update biDir accordingly
        config["biDir"] = 1;
        print("Update: biDir=1");
      end
    end
    
  end    
    
end

-- ################### END CONFIGURATION ######################



-- +++++++++++++++++++++++++ FUNCTION ++++++++++++++++++++++++++++
-- Output file check
-- file_name string - output filename check to
function file_check (file_name)
  file_found = io.open(file_name, "r");
  
  if file_found==nil
  then
    print(file_name .. " does not exists. Write initial head data " ..
          "into the file\n");
   
    return true;
  else
    print(file_name .. " exists so unecessary data will not be written again\n");
    return false;
  end
end
-- ====================== END FUNCTION ========================



-- +++++++++++++++++++++++++ FUNCTION ++++++++++++++++++++++++++++

function start_measurement ()
  
  traffic = config["trafficType"] .. "." .. config["packetSize"];
  
  if tonumber(config["measurementDuration"]) ~= 0
  then
    estimated_time = number_of_packetsizes * tonumber(config["measurementDuration"]) +
    number_of_packetsizes*6;
    -- reducing factor for estimated time - the following should be multiplied
    -- in each iteration of the loop below
    reduce_factor = tonumber(config["measurementDuration"]) + 6;
    infinite_measurement = false;
  else
    estimated_time = "INFINITE"
    infinite_measurement = true;
  end
  
  print("Estimated time needed for this measurement is: " .. estimated_time .. 
  " seconds");

  
  -- print("FILE CHECK");
  -- check output file existence    
  file_exists=file_check("nfpa.".. traffic .. "bytes.res");
  
  
  -- create file descriptor for output
  local file = io.open("nfpa.".. traffic .. "bytes.res","a");

  -- set default output file to the created file descriptor
  io.output(file);
  
  
  -- start sending packets    
  pktgen.start(tonumber(config["sendPort"]));
  -- set the other port as well if biDir is set
  if(tonumber(config["biDir"]) == 1)
  then
    -- start traffic on the other port as well
    pktgen.start(tonumber(config["recvPort"]));
  end


  -- print out results to file
  -- if file already exists, no header information is required
  if(file_exists)
  then
    -- write out actual size as a keyword to the file in order to know
    -- some basic information when later the file is analyzed
    -- and add theoretical max value for the given packet size
    -- io.write(size .. "\n");
    
    io.write("#Snt(pps)|Rcv(pps)|Miss(pps)|Snt(bps)|Rcv(bps)|" ..
             "Diff(bps)");
    -- make header other port's traffic as well if biDir is set
    if(tonumber(config["biDir"]) == 1)
    then
      io.write("|Snt2(pps)|Rcv2(pps)|Miss2(pps)|Snt2(bps)|Rcv2(bps)|" ..
                "Diff2(bps)");
    end
    
    io.write("\n");
  end             
  -- print out results to the console as well
  -- print("Results for: " .. size .. "byte packets\n");
  

  -- wait some seconds to avoid slow start
  print("Waiting for heating up\n");
  sleep(3);

  if(tonumber(config["biDir"]) == 1)
    then
      print("Bi-directional measurement started with " .. traffic .. 
            " bytes packets\n");
    else
      print("Measurement started with " .. traffic .. " bytes packets\n");      
    end  
  -- print("Go grab a coffee...");

  -- loop according to measurement_duration, in each cycle 1 sec sleep is 
  -- invoked, and in each iteration we measure the sending pkts/s rate and the
  -- received pkts/s rate and print them out
  -- infinite loop by default, and will break if measurementDuration 
  -- was set properly
  i = 0;
  m = tonumber(config["measurementDuration"]);
  while true
  do
    if((infinite_measurement == false) and
      (i == m))
    then
      -- break the infinite loop
      break;
    end
    -- get port data
    portRates = pktgen.portStats("all", "rate");
    -- get sent packet/s data
    sent_pkts = portRates[tonumber(config["sendPort"])].pkts_tx;
    -- calculate sending throughput in mbps
    sent_bps = math.floor(sent_pkts*(config["packetSize"]+20)*8);
    -- get received packet/s data
    recv_pkts = portRates[tonumber(config["recvPort"])].pkts_rx;
    -- calculate receiving throughput in mbps    
    recv_bps = math.floor(recv_pkts*(config["packetSize"]+20)*8);
    

    -- calculate the number of missing packets
    miss_pkts = sent_pkts - recv_pkts;
    -- calculate the difference between sent and received mbit/s
    diff_bps = sent_bps - recv_bps;
  
    

    -- log data into file
    -- prettify output
    io.write(sent_pkts .. "|" .. recv_pkts ..  "|".. miss_pkts .. "|" .. 
             sent_bps ..  "|" .. recv_bps .. "|" .. diff_bps);
    
    -- capture bidirectional traffic as well if biDir was set
    if(tonumber(config["biDir"]) == 1)
    then
      -- get sent packet/s data
      sent_pkts2 = portRates[tonumber(config["recvPort"])].pkts_tx;
      -- calculate sending throughput in mbps
      sent_bps2 = math.floor(sent_pkts2*(config["packetSize"]+20)*8);
      -- get received packet/s data
      recv_pkts2 = portRates[tonumber(config["sendPort"])].pkts_rx;
      -- calculate receiving throughput in mbps    
      recv_bps2 = math.floor(recv_pkts2*(config["packetSize"]+20)*8);  
      -- calculate the number of missing packets
      miss_pkts2 = sent_pkts2 - recv_pkts2;
      -- calculate the difference between sent and received mbit/s
      diff_bps2 = sent_bps2 - recv_bps2;
      -- log data into file
      -- prettify output
      io.write("|" .. sent_pkts2 .. "|" .. recv_pkts2 ..  "|".. miss_pkts2 
              .. "|" .. sent_bps2 ..  "|" .. recv_bps2 .. "|" .. diff_bps2);      
    end
                     
               
      io.write("\n");
        
    sleep(1);
    i = i + 1;
  end

  -- stop traffic
  pktgen.stop(tonumber(config["sendPort"]));
  
  -- stop traffic on the other port if biDir was set
  if(tonumber(config["biDir"]) == 1)
  then
    pktgen.stop(tonumber(config["recvPort"]));    
  end
  -- wait some seconds to reach 0 traffic
  print("Cooling down\n")
  sleep(3);
  
  
  io.close(file);
  
  -- print("Estimated time left for this measurement is: " .. estimated_time);

end
-- ====================== END FUNCTION ========================






-- ##################### MAIN ###################
-- reset everything
-- clear pktgen's current stats
pktgen.clear("all");
pktgen.cls();
pktgen.screen("off");
sleep(1);
pktgen.screen("on");

-- read the config
read_config_file();
-- parsing config and check every variable is set correctly
parse_config();




-- Start measurement
-- RESULTS WILL BE WRITTEN TO OUTPUT FILES
start_measurement();

print("Exiting...");
-- switching screen off, since w/o this exiting pktgen influences the terminal
-- and only the half of it can be used!
pktgen.screen("off");

sleep(1);
-- pktgen.quit();
os.exit();



