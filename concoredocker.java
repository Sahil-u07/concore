import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.Map;
import java.util.ArrayList;
import java.util.List;

public class concoredocker {
    private static Map<String, Object> iport = new HashMap<>();
    private static Map<String, Object> oport = new HashMap<>();
    private static String s = "";
    private static String olds = "";
    private static int delay = 1;
    private static int retrycount = 0;
    private static String inpath = "/in";
    private static String outpath = "/out";
    private static Map<String, Object> params = new HashMap<>();
    private static int simtime = 0;
    private static int maxtime;

    public static void main(String[] args) {
        try {
            iport = parseFile("concore.iport");
        } catch (IOException e) {
            e.printStackTrace();
        }
        try {
            oport = parseFile("concore.oport");
        } catch (IOException e) {
            e.printStackTrace();
        }

        try {
            String sparams = new String(Files.readAllBytes(Paths.get(inpath + "1/concore.params")));
            if (sparams.charAt(0) == '"') { // windows keeps "" need to remove
                sparams = sparams.substring(1);
                sparams = sparams.substring(0, sparams.indexOf('"'));
            }
            if (!sparams.equals("{")) {
                System.out.println("converting sparams: " + sparams);
                sparams = "{'" + sparams.replaceAll(",", ",'").replaceAll("=", "':").replaceAll(" ", "") + "}";
                System.out.println("converted sparams: " + sparams);
            }
            try {
                // literalEval returns a proper Map for "{...}"
                params = (Map<String, Object>) literalEval(sparams); 
            } catch (Exception e) {
                System.out.println("bad params: " + sparams);
            }
        } catch (IOException e) {
            params = new HashMap<>();
        }

        defaultMaxTime(100);
    }

    @SuppressWarnings("unchecked")
    private static Map<String, Object> parseFile(String filename) throws IOException {
        String content = new String(Files.readAllBytes(Paths.get(filename)));
        return (Map<String, Object>) literalEval(content); // Casted to Map
    }

    private static void defaultMaxTime(int defaultValue) {
        try {
            String content = new String(Files.readAllBytes(Paths.get(inpath + "1/concore.maxtime")));
            maxtime = ((Number) literalEval(content)).intValue();
        } catch (IOException | ClassCastException | NumberFormatException e) {
            maxtime = defaultValue;
        }
    }

    private static boolean unchanged() {
        if (olds.equals(s)) {
            s = "";
            return true;
        }
        olds = s;
        return false;
    }

    private static Object tryParam(String n, Object i) {
        if (params.containsKey(n)) {
            return params.get(n);
        } else {
            return i;
        }
    }

    private static Object read(int port, String name, String initstr) {
        try {
            String ins = new String(Files.readAllBytes(Paths.get(inpath + port + "/" + name)));
            while (ins.length() == 0) {
                Thread.sleep(delay);
                ins = new String(Files.readAllBytes(Paths.get(inpath + port + "/" + name)));
                retrycount++;
            }
            s += ins;
            List<?> inval = (List<?>) literalEval(ins);
            simtime = Math.max(simtime, ((Number) inval.get(0)).intValue());
            Object[] val = new Object[inval.size() - 1];
            for (int i = 1; i < inval.size(); i++) {
                val[i - 1] = inval.get(i);
            }
            return val;
        } catch (IOException | InterruptedException | ClassCastException e) {
            return initstr;
        }
    }

    private static void write(int port, String name, Object val, int delta) {
        try {
            String path = outpath + port + "/" + name;
            StringBuilder content = new StringBuilder();
            if (val instanceof String) {
                Thread.sleep(2 * delay);
            } else if (!(val instanceof Object[])) {
                System.out.println("write must have list or str");
                return;
            }
            if (val instanceof Object[]) {
                Object[] arrayVal = (Object[]) val;
                content.append("[")
                        .append(simtime + delta)
                        .append(",")
                        .append(arrayVal[0]);
                for (int i = 1; i < arrayVal.length; i++) {
                    content.append(",")
                            .append(arrayVal[i]);
                }
                content.append("]");
                simtime += delta;
            } else {
                content.append(val);
            }
            Files.write(Paths.get(path), content.toString().getBytes());
        } catch (IOException | InterruptedException e) {
            System.out.println("skipping" + outpath + port + "/" + name);
        }
    }

    private static Object[] initVal(String simtimeVal) {
        Object[] val = new Object[] {};
        try {
            List<?> inval = (List<?>) literalEval(simtimeVal);
            simtime = ((Number) inval.get(0)).intValue();
            val = new Object[inval.size() - 1];
            for (int i = 1; i < inval.size(); i++) {
                val[i - 1] = inval.get(i);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return val;
    }

    // custom parser
    private static Object literalEval(String s) {
        s = s.trim();
        if (s.startsWith("{") && s.endsWith("}")) {
            Map<String, Object> map = new HashMap<>();
            String content = s.substring(1, s.length() - 1);
            if (content.isEmpty()) return map;
            for (String pair : content.split(",")) {
                String[] kv = pair.split(":");
                if (kv.length == 2) map.put((String) parseVal(kv[0]), parseVal(kv[1]));
            }
            return map;
        } else if (s.startsWith("[") && s.endsWith("]")) {
            List<Object> list = new ArrayList<>();
            String content = s.substring(1, s.length() - 1);
            if (content.isEmpty()) return list;
            for (String val : content.split(",")) {
                list.add(parseVal(val));
            }
            return list;
        }
        return parseVal(s);
    }

    // helper: Converts Python types to Java primitives
    private static Object parseVal(String s) {
        s = s.trim().replace("'", "").replace("\"", "");
        if (s.equalsIgnoreCase("True")) return true;
        if (s.equalsIgnoreCase("False")) return false;
        if (s.equalsIgnoreCase("None")) return null;
        try { return Integer.parseInt(s); } catch (NumberFormatException e1) {
            try { return Double.parseDouble(s); } catch (NumberFormatException e2) { return s; }
        }
    }
}