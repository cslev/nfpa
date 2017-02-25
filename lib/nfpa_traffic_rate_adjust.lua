package.path = package.path ..";?.lua;test/?.lua;app/?.lua;"


require "Pktgen";



-- ################### CONFIGURATION PART ########################

-- for config params read from the config file

-- local variables for config parameters (read from config.cfg)
config = {};
-- local variable for different packet sizes (read from config.cfg)
pktSizes = {};


-- setting sending rate to 100% at the beginning
-- rate for port 1
sending_rate_1=100;
scale_factor_1=sending_rate;
last_sending_rate_1=sending_rate;
-- rate for port 2
sending_rate_2=100;
scale_factor_2=sending_rate;
last_sending_rate_2=sending_rate;



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
        -- packetSize fields found
      if(key == "packetSize")
      then
        -- store desired packet sizes
        table.insert(pktSizes, value);
      end
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


-- since measurement now is not bounded by a measurementDuration from
-- nfpa.cfg, and might a certain scenario is not configured correctly,
-- this scipt would never quit
-- For this very reason, we create a simple variable, which stores how
-- many times this measure2() was called.
-- if it was called more than 3 times, and the recv_avg values are 0, 
-- then we need to quit!
measure2_called = 0;


-- +++++++++++++++++++++++++ FUNCTION ++++++++++++++++++++++++++++
function measure2 ()
  -- increase measure counter
  measure2_called = measure2_called + 1;

  sent_avg=0;
  recv_avg=0;
  
  -- measure time in seconds (i.e., the seconds a measurement with a 
  -- certain sending_rate lasts
  measure_time=3;
  
  -- kind of a warm up for the changed sending_rate
  print("Tuning in with sending rate ".. sending_rate_1 .."% for 3 secs" 
        .. "on port" .. config["sendPort"] .. "\n");
  
  -- check whether bidirectional scenario is set up
  if(tonumber(config["biDir"]) == 1)
  then
    print("Tuning in with sending rate ".. sending_rate_2 .."% for 3 secs" 
        .. "on port" .. config["recvPort"] .. "\n");
    -- create send/recv avg variables for the other direction as well
    sent_avg_2=0;
    recv_avg_2=0;
  end
  sleep(3);
  
  print("Tuned in! -> Measure");
  for i=1,measure_time
  do
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


    sent_avg=sent_avg + sent_pkts;
    recv_avg=recv_avg + recv_pkts;
    
    -- capture bidirectional traffic as well if biDir was set
    if tonumber(config["biDir"]) == 1
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

      send_avg_2 = sent_avg_2 + sent_pkts2;
      recv_avg_2 = recv_avg_2 + recv_pkts2;

    end

                     
               
    io.write("\n");
          
    -- practically write out each line into the file in each seconds
    -- instead of only writing the results when measurement is done
    io.flush();
    
    sleep(1);
  end
  
  -- calculate averages according to the seconds one measurement lasted
  sent_avg=math.floor(sent_avg/measure_time);
  recv_avg=math.floor(recv_avg/measure_time);
  
  
  -- bidirectional case
  if(tonumber(config["biDir"]) == 1)
  then
    sent_avg_2 = math.floor(sent_avg_2/measure_time);
    recv_avg_2 = math.floor(recv_avg_2/measure_time);
  end
  
  if measure2_called > 3
  then
    --check recv values to see whether VNF was configured properly
    if recv_avg == 0
    then
      print("There is not packets received on port " .. 
            config["recvPort"] .. "! - EXITING...");
      os.exit(-2);
    end
    
    if tonumber(config["biDir"]) == 1 and recv_avg_2 == 0
    then
      print("There is not packets received on port " .. 
            config["sendPort"] .. "! - EXITING...");
      os.exit(-2);
    end
  
  end
  
end
-- ====================== END FUNCTION ========================


-- +++++++++++++++++++++++++ FUNCTION ++++++++++++++++++++++++++++
function change_rate (port, exact, increase)
-- adjusting rates for port - if exact is -1, reducing always by the
-- base factor, otherwise rate is set to the value of exact
  
  -- according to this variable the checking for biDir use case is simpler
  port_1 = false;
  
  if port == tonumber(config["sendPort"])
  then
    -- uni-dir scenario
    last_sending_rate_1 = sending_rate_1;
    port_1 = true;
    scale_factor_1=math.floor(scale_factor_1/2);
  else
    -- bi-dir scenario
    last_sending_rate_2 = senging_rate_2;
    scale_factor_2=math.floor(scale_factor_2/2);
  end
  -- binary search's next step for the best rate
  if exact == -1
  then
    if increase == false
    then
      if port_1
      then
        sending_rate_1 = sending_rate_1 - scale_factor_1;
      else
        sending_rate_2 = sending_rate_2 - scale_factor_2;
      end
    else
      if port_1
      then
        sending_rate_1 = sending_rate_1 + scale_factor_1;
      else
        sending_rate_2 = sending_rate_2 + scale_factor_2;
      end
    end
  else
    if port_1
    then
      sending_rate = exact;
    else
      sending_rate_2 = exact;
    end
  end
  
  -- changing the sending rate exactly to a value
  if port_1
  then
    pktgen.set(port,"rate", sending_rate);
  else
    pktgen.set(port,"rate", sending_rate_2);
  end
  
end
-- ====================== END FUNCTION ========================

-- +++++++++++++++++++++++++ FUNCTION ++++++++++++++++++++++++++++

function start_measurement ()
  
  traffic = config["trafficType"] .. "." .. config["packetSize"];
  -- get the number of desired packet sizes used for measurement
  number_of_packetsizes = #pktSizes;
  -- calculating estimated measurement duration
  -- heating up=3s, cooldown=3s, config["measurementDuration"], number_of_packetsizes
  estimtated_time = " less than a minute!"
  if tonumber(config["measurementDuration"]) ~= 0
  then

    infinite_measurement = false;
  else
    estimated_time = "INFINITE"
    infinite_measurement = true;
  end
  
  print("Estimated time needed for this traffic trace is: " .. estimated_time ..
  " seconds");

  
  -- print("FILE CHECK");
  -- check output file existence    
  file_exists=file_check("nfpa.".. traffic .. "bytes.res");
  
  
  -- create file descriptor for output
  local file = io.open("nfpa.".. traffic .. "bytes.res","a");

  -- set default output file to the created file descriptor
  io.output(file);
  
  -- set initial sending rate for send port
  pktgen.set(tonumber(config["sendPort"],"rate", sending_rate));

  -- start sending packets    
  pktgen.start(tonumber(config["sendPort"]));
  -- set the other port as well if biDir is set
  if(tonumber(config["biDir"]) == 1)
  then
    -- set initial sending rate for the other port as well
    pktgen.set(tonumber(config["recvPort"],"rate", sending_rate_2));
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
  --~ print("Waiting for heating up\n");
  --~ sleep(3);

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
  sending_rate_found_1 = false;
  
  sending_rate_found_2 = false;
  -- if biDir is not set, then we set this variable to true for easing
  -- further checks below
  if tonumber(config["biDir"]) == 0
  then
    sending_rate_2 = true;
  end
  
  
  sending_rate_found = false;
  error_rate = 0.01
  while not sending_rate_found and infinite_measurement 
  do
    -- miss and rate values for port 1
    miss_avg  = sent_avg - recv_avg;
    threshold = sent_avg * error_rate;
    
    print("Threshold:" .. threshold);
    if tonumber(config["biDir"]) == 1
    then
        -- miss and rate values for port 2
      miss_avg_2 = sent_avg_2 - recv_avg_2;
      threshold_2 = sent_avg_2 * error_rate;
      print("Threshold for othe port:" .. threshold_2);
    end  
    
  --~ print("Sending rate: " .. sending_rate);

  -- if sending_rate is altering among 2 values that are next to each 
  -- other, we quit!
    if math.abs(sending_rate_1 - last_sending_rate_1) == 1
    then
      print("We reached a possibly good sending rate for port " ..
            config["sendPort"]);
      sending_rate_1=sending_rate_1+1; -- increase sending rate the greater value
      change_rate(tonumber(config["sendPort"]),sending_rate_1,false);
      measure2();
      sending_rate_found_1 = true;
    else
    
      -- check threshold
      if threshold < miss_avg
      then
        -- recv and sent are still too far from each other
        print("Threshold not met! -- still adjusting");
        change_rate(tonumber(config["sendPort"]),-1,false);
        measure2();
        
      else
        -- threshold reached - we may jumped to much, check greater rate
        print("Threshold  for port ".. config["sendPort"] .. " met...");
        if sending_rate_1 > 99
        then
          print("Best sending rate for port " .. config["sendPort"] ..
                "was 100%...measuring this rate...");
          measure2();
          sending_rate_found_1 = true;
          
          if tonumber(config["biDir"]) == 0
          then
            sending_rate_found = true;
          end
        else
          change_rate(tonumber(config["sendPort"]),-1,true);
          measure2();
        end
      end
    end

      -- BiDir scenario
      if tonumber(config["biDir"]) == 1
      then
        if math.abs(sending_rate_2 - last_sending_rate_2) == 1
        then
          print("We reached a possibly good sending rate for port " ..
                config["sendPort"]);
          sending_rate_2=sending_rate_2+1; -- increase sending rate the greater value
          change_rate(tonumber(config["recvPort"]),sending_rate_2,false);
          measure2();
          sending_rate_found_2 = true;
        else
          -- check threshold
          if threshold_2 < miss_avg_2
          then
            -- recv and sent are still too far from each other
            print("Threshold not met! -- still adjusting");
            change_rate(tonumber(config["recvPort"]),-1,false);
            measure2();
          else
            -- threshold reached - we may jumped to much, check greater rate
            print("Threshold  for port ".. config["sendPort"] .. " met...");
            if sending_rate_2 > 99
            then
              print("Best sending rate for port " .. config["recvPort"] ..
                    "was 100%...measuring this rate...");
              measure2();
              sending_rate_found_2 = true;
            else
              change_rate(tonumber(config["recvPort"]),-1,true);
              measure2();
            end
          end
        end
      end
      

  
    -- this will stop the loop
    if sending_rate_found_1 and sending_rate_found_2
    then
      sending_rate_found = true;
    end

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



