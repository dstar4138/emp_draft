/**
 * Simpler Java Interface example for SMTG
 *
 * Please read the README for more information.
 *
 * @author Alexander Dean
 **/
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.net.Socket;

//you can use any JSON library as long as you follow the message syntax
//import org.json.JSONObject;
import java.util.Arrays;

public class jsmtg_t{
    
	//Daemon Config
	public static final String HOST_IP = "localhost";
	public static final int HOST_PORT = 8080;
	
    //Socket stuffs
    private static Socket socket = null;
    private static BufferedReader in = null;
    private static BufferedWriter out = null;
    

    public static String getID(String json){
	String[] tokens = json.split("[\",:{}]+");
	System.out.println(Arrays.toString(tokens));
	int count = 0;
	for(String token : tokens){
	    if( token.equals("dest") ){
		return tokens[count+1];
	    }
	    count++;
	}
	return "null";
    }

    public static void main(String[] args) throws Exception{
 
    	//1. CONNECTION
	System.out.println("Connecting");
    	socket = new Socket(HOST_IP, HOST_PORT);	

    	//2. GET STREAM INFO
    	//  notice the streams are being read as a UTF byte stream.
        in = new BufferedReader(new InputStreamReader(socket.getInputStream(), "UTF8"));
        out = new BufferedWriter(new OutputStreamWriter(socket.getOutputStream(), "UTF8"));
        	
    	//3. WAIT FOR RESPONSE, ITS YOUR ID!!
	while(!in.ready()){}
	String response = "";
    	while(in.ready()){
		response+=(char)in.read();
	}
	System.out.println("Got response: "+response);
	
	//Use a JSON library or make your own.
	String id=getID(response);
	System.out.println("Parsed ID: "+id);
    	
    	//4a. SEND COMMANDS
    	out.write("{\"message\":\"cmd\",\"command\":\"status\",\"source\":\""+id+"\",\"dest\":null}");
    	out.flush();
    	
    	//4b. WAIT & GET RESPONSE
    	while(!in.ready()){}
    	String status = "";
    	while(in.ready()){
    		status += (char)in.read();
    	}
    	
    	//AND THATS IT!!
    	/* Steps 4a and 4b are normally in a loop, or can be repeated 
    	 * once the connection is made. 
    	 * 
    	 * Also note that normally step 3 doesn't take too long, but if there
    	 * is a problem with the connection, or the daemon doesnt think you
    	 * are registered. It will drop its end of the connection. This may
    	 * cause it to hang.
    	 */
    	
    	System.out.println("stats received: "+status);
    }
}
