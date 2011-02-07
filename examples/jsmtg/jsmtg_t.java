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

public class jsmtg_t{
    
	//Daemon Config
	public static final String HOST_IP = "localhost";
	public static final int HOST_PORT = 8080;
	
    //Socket stuffs
    private static Socket socket = null;
    private static BufferedReader in = null;
    private static BufferedWriter out = null;
    
    public static void main(String[] args) throws Exception{
 
    	//1. CONTECTION
    	socket = new Socket(HOST_IP, HOST_PORT);

    	//2. GET STREAM INFO
    	//  notice the streams are being read as a UTF byte stream.
        in = new BufferedReader(new InputStreamReader(socket.getInputStream(), "UTF8"));
        out = new BufferedWriter(new OutputStreamWriter(socket.getOutputStream(), "UTF8"));
    	
        //3. SEND INTERFACE ID
    	out.write("i00000001"); 
    	out.flush();
    	
    	//4. WAIT FOR RESPONSE
    	while(!in.ready()){}
    	
    	//5. PUSH RESPONSE OUT OF BUFFER INTO STRING
    	String output = "";
    	while(in.ready()){
    		output += (char)in.read();
    	}
    	
    	//6a. SEND COMMANDS
    	out.write("stats");
    	out.flush();
    	
    	//6b. WAIT & GET RESPONSE
    	while(!in.ready()){}
    	String stats = "";
    	while(in.ready()){
    		stats += (char)in.read();
    	}
    	
    	//AND THATS IT!!
    	/* Steps 6a and 6b are normally in a loop, or can be repeated 
    	 * once the connection is made. 
    	 * 
    	 * Also note that normally step 4 doesn't take too long, but if there
    	 * is a problem with the connection, or the daemon doesnt think you
    	 * are registered. It will drop its end of the connection. This may
    	 * cause it to hang.
    	 */
    	
    	System.out.println("stats received: "+stats);
    }
}