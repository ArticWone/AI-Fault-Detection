package com.smi.webui;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.net.ConnectivityManager;
import android.net.Network;
import android.net.NetworkCapabilities;
import android.net.Uri;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.view.Window;
import android.view.WindowInsets;
import android.webkit.PermissionRequest;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.EditText;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

public class MainActivity extends Activity {
    private static final String PREFS = "smi_webui";
    private static final String KEY_URL = "webui_url";

    private WebView webView;
    private ProgressBar progressBar;
    private TextView statusText;
    private SharedPreferences prefs;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        Window window = getWindow();
        window.setStatusBarColor(getColor(R.color.smi_panel));
        window.setNavigationBarColor(getColor(R.color.smi_panel));
        prefs = getSharedPreferences(PREFS, MODE_PRIVATE);
        buildLayout();
        configureWebView();
        loadSavedUrl();
    }

    @SuppressLint("SetJavaScriptEnabled")
    private void configureWebView() {
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setMediaPlaybackRequiresUserGesture(false);
        settings.setLoadWithOverviewMode(true);
        settings.setUseWideViewPort(true);
        settings.setBuiltInZoomControls(true);
        settings.setDisplayZoomControls(false);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_COMPATIBILITY_MODE);

        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onProgressChanged(WebView view, int newProgress) {
                progressBar.setProgress(newProgress);
                progressBar.setVisibility(newProgress >= 100 ? View.GONE : View.VISIBLE);
            }

            @Override
            public void onPermissionRequest(PermissionRequest request) {
                request.grant(request.getResources());
            }
        });

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageFinished(WebView view, String url) {
                statusText.setText(url);
                view.evaluateJavascript(appOnlyLayoutScript(), null);
            }

            @Override
            public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                if (request.isForMainFrame()) {
                    statusText.setText("Web UI unreachable");
                }
            }
        });
    }

    private void buildLayout() {
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setBackgroundColor(getColor(R.color.smi_bg));
        root.setPadding(0, statusBarHeight(), 0, 0);

        LinearLayout toolbar = new LinearLayout(this);
        toolbar.setGravity(Gravity.CENTER_VERTICAL);
        toolbar.setPadding(dp(10), dp(5), dp(10), dp(5));
        toolbar.setBackgroundColor(getColor(R.color.smi_panel));

        TextView title = new TextView(this);
        title.setText("SMI Web UI");
        title.setTextColor(getColor(R.color.smi_ink));
        title.setTextSize(16);
        title.setTypeface(title.getTypeface(), android.graphics.Typeface.BOLD);
        toolbar.addView(title, new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1));

        toolbar.addView(actionButton("Reload", v -> webView.reload()));
        toolbar.addView(actionButton("URL", v -> promptForUrl()));
        toolbar.addView(actionButton("Open", v -> openExternal()));

        statusText = new TextView(this);
        statusText.setSingleLine(true);
        statusText.setTextColor(getColor(R.color.smi_muted));
        statusText.setTextSize(11);
        statusText.setPadding(dp(10), dp(2), dp(10), dp(4));
        statusText.setBackgroundColor(getColor(R.color.smi_panel));

        FrameLayout content = new FrameLayout(this);
        webView = new WebView(this);
        content.addView(webView, new FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.MATCH_PARENT,
                FrameLayout.LayoutParams.MATCH_PARENT
        ));

        progressBar = new ProgressBar(this, null, android.R.attr.progressBarStyleHorizontal);
        progressBar.setMax(100);
        progressBar.setVisibility(View.GONE);
        content.addView(progressBar, new FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.MATCH_PARENT,
                dp(3),
                Gravity.TOP
        ));

        root.addView(toolbar, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
        ));
        root.addView(content, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                0,
                1
        ));
        setContentView(root);
    }

    private TextView actionButton(String label, View.OnClickListener listener) {
        TextView button = new TextView(this);
        button.setText(label);
        button.setGravity(Gravity.CENTER);
        button.setTextColor(Color.WHITE);
        button.setTypeface(button.getTypeface(), android.graphics.Typeface.BOLD);
        button.setBackgroundColor(getColor(R.color.smi_accent));
        button.setTextSize(13);
        button.setPadding(dp(8), dp(5), dp(8), dp(5));
        button.setOnClickListener(listener);
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
        );
        params.setMargins(dp(8), 0, 0, 0);
        button.setLayoutParams(params);
        return button;
    }

    private void loadSavedUrl() {
        String fallback = getString(R.string.default_webui_url);
        String url = prefs.getString(KEY_URL, fallback);
        if (!isNetworkAvailable()) {
            Toast.makeText(this, "No network connection", Toast.LENGTH_LONG).show();
        }
        loadUrl(url);
    }

    private void loadUrl(String rawUrl) {
        String url = normalizeUrl(rawUrl);
        prefs.edit().putString(KEY_URL, url).apply();
        statusText.setText(url);
        webView.loadUrl(url);
    }

    private void promptForUrl() {
        EditText input = new EditText(this);
        input.setSingleLine(true);
        input.setText(prefs.getString(KEY_URL, getString(R.string.default_webui_url)));
        input.setSelectAllOnFocus(true);
        input.setHint(getString(R.string.default_webui_url));

        new AlertDialog.Builder(this)
                .setTitle("Web UI address")
                .setView(input)
                .setPositiveButton("Load", (dialog, which) -> loadUrl(input.getText().toString()))
                .setNegativeButton("Cancel", null)
                .show();
    }

    private void openExternal() {
        String url = prefs.getString(KEY_URL, getString(R.string.default_webui_url));
        startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(url)));
    }

    private String normalizeUrl(String rawUrl) {
        String url = rawUrl == null ? "" : rawUrl.trim();
        if (url.isEmpty()) {
            url = getString(R.string.default_webui_url);
        }
        if (!url.startsWith("http://") && !url.startsWith("https://")) {
            url = "http://" + url;
        }
        return url;
    }

    private String appOnlyLayoutScript() {
        String address = displayAddress(prefs.getString(KEY_URL, getString(R.string.default_webui_url)));
        return "(function(){"
                + "if(document.getElementById('smi-android-app-css'))return;"
                + "var s=document.createElement('style');"
                + "s.id='smi-android-app-css';"
                + "s.textContent='"
                + "header{position:static!important;padding:6px 10px!important;gap:3px!important;}"
                + "header h1{font-size:22px!important;}"
                + ".subtitle{font-size:13px!important;margin-top:1px!important;}"
                + "main{padding:8px 10px 92px!important;}"
                + ".summary{display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:8px!important;margin-bottom:8px!important;}"
                + ".summary-panel{min-height:82px!important;padding:9px!important;}"
                + ".summary-title,.label{font-size:10px!important;line-height:1.15!important;margin-bottom:5px!important;}"
                + ".summary-value{font-size:21px!important;line-height:1.08!important;}"
                + ".summary-meta{font-size:11px!important;line-height:1.2!important;margin-top:5px!important;}"
                + ".grid{display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:8px!important;margin-bottom:12px!important;}"
                + ".card,.card-button{min-height:74px!important;padding:9px!important;}"
                + ".card-button{border-radius:8px!important;}"
                + ".card-button.centered{display:flex!important;align-items:center!important;justify-content:center!important;text-align:center!important;}"
                + ".value{font-size:26px!important;line-height:1.05!important;}"
                + ".card-button.bad-packs .value{font-size:20px!important;line-height:1.05!important;}"
                + ".status{min-height:44px!important;padding:6px 9px!important;margin-top:-2px!important;font-size:13px!important;align-items:center!important;}"
                + ".status .dot{flex:0 0 auto!important;align-self:center!important;}"
                + ".smi-status-lines{display:flex!important;flex-direction:column!important;justify-content:center!important;gap:2px!important;line-height:1.15!important;min-width:0!important;}"
                + ".smi-status-main{white-space:normal!important;word-break:break-word!important;}"
                + ".smi-status-time{font-size:11px!important;color:var(--muted)!important;font-weight:700!important;}"
                + ".section-header{gap:6px!important;margin-top:2px!important;}"
                + ".section-title{margin:4px 0 6px!important;font-size:21px!important;}"
                + ".viewer,.viewer iframe{min-height:300px!important;height:300px!important;}"
                + ".camera-grid{display:grid!important;grid-template-columns:1fr!important;gap:8px!important;margin-bottom:12px!important;}"
                + "#camera-preview{margin-top:4px!important;}"
                + ".camera-panel{border-radius:7px!important;max-width:100%!important;}"
                + ".camera-panel iframe{width:100%!important;height:clamp(190px,38vh,360px)!important;aspect-ratio:auto!important;}"
                + ".camera-meta{align-items:center!important;padding:7px 10px!important;font-size:12px!important;gap:6px!important;}"
                + ".camera-card-actions{gap:6px!important;}"
                + ".camera-admin-link{min-height:26px!important;padding:4px 8px!important;font-size:12px!important;}"
                + ".shutdown-dock{padding:7px 10px calc(7px + env(safe-area-inset-bottom))!important;}"
                + ".shutdown-button{min-height:36px!important;font-size:12px!important;}"
                + ".confirm-modal{padding:14px!important;}"
                + "';"
                + "document.head.appendChild(s);"
                + "var address='" + address + "';"
                + "function escapeHtml(value){return value.replace(/[&<>\\\"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','\\\"':'&quot;',\"'\":'&#39;'}[c];});}"
                + "function combineStatus(){"
                + "var status=document.getElementById('status');"
                + "if(!status||status.dataset.smiFormatting==='1'||status.querySelector('.smi-status-time'))return;"
                + "var text=status.textContent.replace(/\\s+/g,' ').trim();"
                + "text=text.replace(address+' - ','');"
                + "var match=text.match(/(\\d{4}-\\d{2}-\\d{2}T[\\d:]+)$/);"
                + "var time=match?match[1]:'';"
                + "var main=match?text.slice(0,match.index).replace(/\\s+-\\s+$/,''):text;"
                + "if(main.indexOf(address)===0){main=main.slice(address.length).replace(/^\\s+-\\s+/,'');}"
                + "status.dataset.smiFormatting='1';"
                + "status.setAttribute('title',address+' - '+text);"
                + "status.innerHTML='<span class=\"dot\"></span><span class=\"smi-status-lines\"><span class=\"smi-status-main\">'+escapeHtml(address+' - '+main)+'</span>'+(time?'<span class=\"smi-status-time\">'+escapeHtml(time)+'</span>':'')+'</span>';"
                + "delete status.dataset.smiFormatting;"
                + "}"
                + "combineStatus();"
                + "var status=document.getElementById('status');"
                + "if(status){new MutationObserver(function(){requestAnimationFrame(combineStatus);}).observe(status,{childList:true,subtree:true,characterData:true});}"
                + "})();";
    }

    private String displayAddress(String url) {
        return normalizeUrl(url)
                .replace("http://", "")
                .replace("https://", "")
                .replaceAll("/+$", "");
    }

    private boolean isNetworkAvailable() {
        ConnectivityManager manager = (ConnectivityManager) getSystemService(Context.CONNECTIVITY_SERVICE);
        if (manager == null) {
            return false;
        }
        Network network = manager.getActiveNetwork();
        if (network == null) {
            return false;
        }
        NetworkCapabilities capabilities = manager.getNetworkCapabilities(network);
        return capabilities != null && capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET);
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }

    private int statusBarHeight() {
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.R) {
            WindowInsets insets = getWindowManager().getCurrentWindowMetrics().getWindowInsets();
            return insets.getInsets(WindowInsets.Type.statusBars()).top;
        }
        int resourceId = getResources().getIdentifier("status_bar_height", "dimen", "android");
        return resourceId > 0 ? getResources().getDimensionPixelSize(resourceId) : dp(24);
    }

    @Override
    public void onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack();
            return;
        }
        super.onBackPressed();
    }
}
