package com.terry.hub;

import android.os.Bundle;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        // 1. 創建一個全螢幕的網頁瀏覽器元件
        WebView webView = new WebView(this);
        setContentView(webView);
        
        // 2. 開啟現代網頁必須要有的 JavaScript 功能
        WebSettings webSettings = webView.getSettings();
        webSettings.setJavaScriptEnabled(true);
        webSettings.setDomStorageEnabled(true);
        
        // 3. 確保點擊網頁內任何連結時，都在這個 App 裡面打開，而不是跳出瀏覽器
        webView.setWebViewClient(new WebViewClient());
        
        // 4. 🔥 注入你的個人分享網站網址（讓它不再是一片空白！）
        webView.loadUrl("https://terry20250224.github.io/my-share/links.html");
    }
}
