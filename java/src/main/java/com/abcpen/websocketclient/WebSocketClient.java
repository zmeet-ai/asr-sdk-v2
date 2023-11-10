import java.io.IOException;
import java.util.concurrent.TimeUnit;

import okhttp3.*;
import okio.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.nio.ByteBuffer;
import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;
import java.io.UnsupportedEncodingException;
import java.security.InvalidKeyException;
import javax.crypto.Mac; 
import javax.crypto.spec.SecretKeySpec;
import java.util.Base64;

public class WebSocketClient {

  private static final Logger logger = LoggerFactory.getLogger(WebSocketClient.class);
  
  private static final String API_URL = "wss://asr-dev.abcpen.com";
  private static final String APP_ID = "test1";
  private static final String APP_SECRET = "2258ACC4-199B-4DCB-B6F3-C2485C63E85A";
  
  private static final int TIME_PER_CHUNK = 100; // ms
  private static final int SAMPLE_RATE = 16000;
  
  public static void main(String[] args) throws IOException, InterruptedException, NoSuchAlgorithmException, InvalidKeyException {

    OkHttpClient client = new OkHttpClient.Builder()
        .writeTimeout(30, TimeUnit.SECONDS)
        .readTimeout(0, TimeUnit.MINUTES) // disable read timeout for streaming
        .build();

    Request request = new Request.Builder()
        .url(getUrlWithAuth())
        .build();

    client.newWebSocket(request, new WebSocketListener() {

      @Override
      public void onOpen(WebSocket webSocket, Response response) {
        // send audio stream
        new Thread(() -> {
          try {
            sendAudioStream(webSocket);
          } catch (IOException e) {
            logger.error("Error sending audio stream", e);
          }
        }).start();

        // receive transcription
        new Thread(new ReceiveTranscriptionThread(webSocket)).start(); 
      }

      @Override 
      public void onFailure(WebSocket webSocket, Throwable t, Response response) {
        logger.error("Error on websocket", t);
      }

    });

    // keep alive
    Thread.sleep(Long.MAX_VALUE); 
  }

  private static String getUrlWithAuth() throws NoSuchAlgorithmException, InvalidKeyException, UnsupportedEncodingException {
    long timestamp = System.currentTimeMillis()/1000;
    String sign = getSignature(APP_ID, timestamp);
    
    return API_URL + "/v2/asr/ws?appid=" + APP_ID 
           + "&ts=" + timestamp
           + "&signa=" + sign
           + "&asr_type=2"
           + "&trans_mode=1"
           + "&target_lang=ru"
           + "&pd=court";
  }

private static String getSignature(String appId, long timestamp) throws NoSuchAlgorithmException, InvalidKeyException, UnsupportedEncodingException {
   String text = appId + timestamp;
   byte[] data = text.getBytes("utf-8");
   
   Mac sha256HMAC = Mac.getInstance("HmacSHA256");
   SecretKeySpec secretKey = new SecretKeySpec(APP_SECRET.getBytes("utf-8"), "HmacSHA256"); 
   sha256HMAC.init(secretKey);

   byte[] hash = sha256HMAC.doFinal(data);
   return Base64.getEncoder().encodeToString(hash);
}

  private static void sendAudioStream(WebSocket webSocket) throws IOException {
    // send audio chunks
    ByteBuffer buffer = getNextAudioChunk(); 
    while (buffer.hasRemaining()) {
      webSocket.send(ByteString.of(buffer));
      buffer = getNextAudioChunk();
      // sleep for TIME_PER_CHUNK ms
    }
  }

  private static ByteBuffer getNextAudioChunk() {
    // read next chunk from audio file
    return ByteBuffer.allocate(0); // dummy
  }

  private static class ReceiveTranscriptionThread implements Runnable {

    private final WebSocket webSocket;

    public ReceiveTranscriptionThread(WebSocket webSocket) {
      this.webSocket = webSocket;
    }

    @Override
    public void run() {
      /*
      try {
        while (true) {
          WebSocketFrame frame = webSocket.receiveFrame();
          String text = frame.text();
          if (text.isEmpty()) {
            break;
          }
          // process transcription response
        }
      } catch (IOException e) {
        logger.error("Error receiving transcription", e);
      }
      */
    }
  }

}