Performance Measurement Guide: File-Based vs. ZeroMQThis guide provides a step-by-step methodology for quantifying and comparing the performance of a multi-node system using two different inter-process communication (IPC) methods:File-Based: Nodes communicate by writing and reading files in shared directories.ZeroMQ-Based: Nodes communicate over high-performance, in-memory messaging sockets.By following these steps, you can generate concrete data on latency, throughput, and resource utilization to demonstrate the impact of migrating from a file-based to a ZMQ-based architecture.PrerequisitesTwo Project Versions: You must have two separate versions of your concore project generator: one that uses the original file-based communication, and one that uses the new ZMQ-based system we developed.Python Libraries: Ensure you have the necessary Python libraries installed. psutil is required for programmatically measuring CPU usage.pip install pyzmq psutil
macOS Command Line Tools: You should be comfortable with basic Terminal commands. The iostat and top commands are used for monitoring.Step 1: Test Environment SetupFirst, create a clean directory structure for your tests.# 1. Create a main directory for the performance tests
mkdir concore_performance_tests
cd concore_performance_tests

# 2. Create a directory to hold the source scripts for the nodes
mkdir source_scripts

# 3. Create a directory for the file-based system output
mkdir file_based_project

# 4. Create a directory for the ZMQ-based system output
mkdir zmq_project
Next, create the following two files inside the concore_performance_tests directory.a) graph.graphmlThis simple 4-node pipeline graph will be used for all tests.<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<graphml xmlns="http://graphml.graphdrawing.org/graphml" xmlns:java="http://www.yworks.com/xml/yfiles-common/1.0/java" xmlns:sys="http://www.yworks.com/xml/yfiles-common/markup/primitives/2.0" xmlns:x="http://www.yworks.com/xml/yfiles-common/markup/2.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:y="http://www.yworks.com/xml/graphml" xmlns:yed="http://www.yworks.com/xml/yed/3" xsi:schemaLocation="http://graphml.graphdrawing.org/graphml http://www.yworks.com/xml/schema/graphml/1.1/ygraphml.xsd">
  <key for="node" id="d0" yfiles.type="nodegraphics"/>
  <key for="edge" id="d1" yfiles.type="edgegraphics"/>
  <graph edgedefault="directed" id="G">
    <node id="n0">
      <data key="d0"><y:ShapeNode><y:NodeLabel>A:producer.py</y:NodeLabel></y:ShapeNode></data>
    </node>
    <node id="n1">
      <data key="d0"><y:ShapeNode><y:NodeLabel>B:processor.py</y:NodeLabel></y:ShapeNode></data>
    </node>
    <node id="n2">
      <data key="d0"><y:ShapeNode><y:NodeLabel>C:processor.py</y:NodeLabel></y:ShapeNode></data>
    </node>
    <node id="n3">
      <data key="d0"><y:ShapeNode><y:NodeLabel>D:consumer.py</y:NodeLabel></y:ShapeNode></data>
    </node>
    <edge id="e0" source="n0" target="n1">
      <data key="d1"><y:PolyLineEdge><y:EdgeLabel>A_to_B</y:EdgeLabel></y:PolyLineEdge></data>
    </edge>
    <edge id="e1" source="n1" target="n2">
      <data key="d1"><y:PolyLineEdge><y:EdgeLabel>B_to_C</y:EdgeLabel></y:PolyLineEdge></data>
    </edge>
    <edge id="e2" source="n2" target="n3">
      <data key="d1"><y:PolyLineEdge><y:EdgeLabel>C_to_D</y:EdgeLabel></y:PolyLineEdge></data>
    </edge>
  </graph>
</graphml>
b) test_data.dat (Large data file for throughput testing)Run this command in your terminal to create a 100MB file.mkfile 100m test_data.dat
Finally, place the sample node scripts (provided in the other documents) into the source_scripts directory.Step 2: Running the Baseline (File-Based) TestsFirst, generate the file-based project using your original mkconcore.py.# Navigate to the project directory
cd file_based_project

# Run mkconcore.py to generate the project
python3 /path/to/your/original/mkconcore.py ../graph.graphml ../source_scripts . posix
Now, run the following tests from within the file_based_project directory.Test 1: Latency / End-to-End TimeThis test measures the time to process 1,000 small messages through the pipeline.Set the test mode in source_scripts/producer.py to 'latency'.Run the test using the time command:./build
time ./run
Record the real time from the output. This is your End-to-End Time.Example: real 0m48.521sCalculate Average Latency: End-to-End Time / 1000 messages.Test 2: ThroughputThis test measures the speed of transferring the 100MB file.Set the test mode in source_scripts/producer.py to 'throughput'.Run the test:./build
time ./run
Record the real time.Calculate Throughput: 100 MB / (time in seconds).Test 3: CPU & Disk I/OThis test monitors system resources during the throughput test. You will need two terminal windows.In Terminal 2, start the disk monitor:iostat -d 1
In Terminal 1, run the throughput test (time ./run).In Terminal 2, watch the MB/s column for your disk (e.g., disk0). Note the peak value.Stop iostat (Ctrl+C). Now start the CPU monitor:top -o cpu
In Terminal 1, run the throughput test again.In Terminal 2, watch the %CPU column for your python processes and note the approximate average value.Step 3: Running the ZeroMQ TestsNow, generate the ZMQ-based project using your new, modified mkconcore.py.# Navigate to the project directory
cd ../zmq_project # Go back up and into the zmq directory

# Run the new mkconcore.py
python3 /path/to/your/new/mkconcore.py ../graph.graphml ../source_scripts . posix
Repeat the exact same three tests as in Step 2 from within the zmq_project directory. Use the ZMQ versions of the sample scripts.Step 4: Analyze the ResultsFill in a table like the one below with your collected data. This will give you a clear, quantitative comparison of the two systems.MetricFile-Based SystemZeroMQ SystemImprovement FactorAvg. LatencyYour value (ms)Your value (ms)CalculateData ThroughputYour value (MB/s)Your value (MB/s)CalculateEnd-to-End TimeYour value (s)Your value (s)CalculateAvg. CPU UsageYour value (%)Your value (%)CalculateDisk WritesYour value (MB)Your value (MB)CalculateThis structured approach will provide undeniable evidence of the performance gains from your architectural improvements.