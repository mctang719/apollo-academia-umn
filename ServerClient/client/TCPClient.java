package client;

import shared.*;

import java.io.*;
import java.net.*;


public class TCPClient {
	String serverIP; //Leave it as string for now, since there is a constructor for it
	int port;
	Socket clientSocket;
	ObjectOutputStream outToServer;
	ObjectInputStream inFromServer;

	BufferedWriter writer;
	String fileName;
	
	public TCPClient(String serverIP, int port) throws IOException
	{
		this.serverIP = serverIP;
		this.port = port;
		createSocket();

		this.outToServer = new ObjectOutputStream(clientSocket.getOutputStream());
		this.inFromServer = new ObjectInputStream(clientSocket.getInputStream());
		this.writer = null;
	}
	
	public void writeToServer(Object obj) throws IOException  
	{
		this.outToServer.writeObject(obj);
	}

	public Boolean getFileFromServer(char[] fileName) throws IOException, ClassNotFoundException
	{
		this.fileName = new String(fileName);

		char[] payload = new char[MsgT.BUFFER_SIZE];

		for(int i = 0; i < fileName.length; i++)
		{
			payload[i] = fileName[i];
		}

		Message getMsg = new Message(MsgT.MSG_TYPE_GET, payload, fileName.length);
		writeToServer(getMsg);
		
		return receiveFromServer();
	}
	
	//This class is the main class that will do all file and packet operations
	public Boolean receiveFromServer() throws IOException, ClassNotFoundException
	{
		Message recv = (Message) inFromServer.readObject(); //deserialize
		System.out.println("client: RX " + recv.getStatus());
		Message send; 
		
		switch(recv.msgType){
			case MsgT.MSG_TYPE_FINISH:

				if(MsgT.DEBUG)
						System.out.println("Downloaded file: " + System.getProperty("user.dir") + "/"+ fileName);

				send = new Message(MsgT.MSG_TYPE_FINISH, new char[0], 0);
				writeToServer(send);
				writer.close();
				return true;
			case MsgT.MSG_TYPE_GET_RESP:
				if(writer == null) //First message, make a file and write out
				{
					// writer = new BufferedWriter(new OutputStreamWriter(
							// new FileOutputStream(fileName, false), "US-ASCII")); //C unsigned chars are ASCII 0-255 
					writer = new BufferedWriter(new FileWriter(fileName, false));
					//use this because our payload is already a char else it flips the bits
				}	
				writer.write(recv.getPayload());

				send = new Message(MsgT.MSG_TYPE_GET_ACK, new char[0], 0);
				writeToServer(send);
				break;
			default:
				System.err.println("CANNOT UNDERSTAND SERVER RESP.");
				throw new UnsupportedOperationException();
		}

		if(send != null && MsgT.DEBUG)
			System.out.println("client: TX " + send.getStatus());

		return receiveFromServer(); //recursively waits for server until we get MSG_TYPE_FINISH
		
		// int count;
		// char[] buffer = new char[8192]; 
		// while ((count = inFromServer.read(buffer)) > 0)
		// {
		//   inFromServer.write(buffer, 0, count);
		// }
	}

	public void createSocket() throws IOException, ConnectException
	{
		System.out.println("Creating socket on host: " + serverIP);
		clientSocket = new Socket(serverIP, port);
		System.out.println("Client Connection Established");
		if(clientSocket.getPort() == 0)
			System.err.println("Socket not connected yet");
	}
	
	public void closeSocket() throws IOException
	{
		clientSocket.close();
	}
	
	

}
