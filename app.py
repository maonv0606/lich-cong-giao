#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Catholic Calendar Web Server (AioHTTP) - Editorial Design
Thiết kế theo chuẩn xuất bản Phụng Vụ cổ điển & hiện đại (Typography-first, No-emoji, Craftsmanship).
"""

import os
import json
import urllib.parse
from aiohttp import web
from generate_calendar import parse_catholic_data, parse_event_details, generate_ics

PORT = 8080
DATA_FILE = "raw_calendar_data.txt"
ICS_FILE = "catholic_calendar_2026.ics"

def reload_events():
    if os.path.exists(DATA_FILE):
        raw_days = parse_catholic_data(DATA_FILE)
        events = [parse_event_details(d) for d in raw_days]
        feasts_only = [ev for ev in events if ev is not None]
        generate_ics(feasts_only, ICS_FILE)
        return feasts_only
    return []

current_events = reload_events()

INDEX_HTML = r"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Lịch Phụng Vụ Công Giáo - Năm Phụng Vụ 2026</title>
  
  <meta property="og:title" content="Lịch Phụng Vụ Công Giáo - Năm Phụng Vụ 2026">
  <meta property="og:description" content="Đồng bộ tự động các ngày Lễ Trọng, Lễ Kính, Lễ Buộc và Bài Đọc Thánh Lễ vào iPhone & Android.">
  <meta property="og:image" content="/static/images/social_card.jpg">
  <meta property="og:type" content="website">
  <link rel="icon" type="image/jpeg" href="/static/images/social_card.jpg">

  <!-- Google Fonts: Be Vietnam Pro (Native Vietnamese Modern Sans) + Lora (Literary Serif) + Playfair Display -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400;1,600&family=Lora:ital,wght@0,500;0,600;0,700;1,500&family=Playfair+Display:ital,wght@0,600;0,700;0,800;1,600&display=swap" rel="stylesheet">

  <style>
    :root {
      --font-heading: 'Be Vietnam Pro', -apple-system, BlinkMacSystemFont, sans-serif;
      --font-body: 'Be Vietnam Pro', -apple-system, BlinkMacSystemFont, sans-serif;

      --bg: #F8F6F1;
      --surface: #FFFFFF;
      --surface-elevated: #FDFDFD;
      --border: #E8E3DA;
      --border-dark: #D8D1C5;
      --text: #1C1A17;
      --text-muted: #666056;
      --text-subtle: #8C8476;
      
      --crimson: #7D1A25;
      --crimson-dark: #5C101A;
      --crimson-light: #F8ECEE;
      --gold: #A67527;
      --gold-light: #F7F1E5;
      --gold-border: #E2CE9B;

      --blue-tag: #1B4B82;
      --blue-bg: #EDF3FA;
      --green-tag: #1E663B;
      --green-bg: #EEF6F1;
      --purple-tag: #5B2C78;
      --purple-bg: #F5EEF9;

      --radius-sm: 6px;
      --radius-md: 12px;
      --radius-lg: 18px;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: var(--font-body);
      background-color: var(--bg);
      color: var(--text);
      line-height: 1.6;
      -webkit-font-smoothing: antialiased;
      padding-bottom: 80px;
    }

    body.font-bevietnam {
      --font-heading: 'Be Vietnam Pro', -apple-system, BlinkMacSystemFont, sans-serif;
      --font-body: 'Be Vietnam Pro', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    body.font-lora {
      --font-heading: 'Lora', Georgia, serif;
      --font-body: 'Be Vietnam Pro', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    body.font-playfair {
      --font-heading: 'Playfair Display', Georgia, serif;
      --font-body: 'Be Vietnam Pro', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* TOP ANNOUNCEMENT / MASTHEAD STRIP */
    .top-strip {
      background: var(--surface);
      border-bottom: 1px solid var(--border);
      padding: 8px 20px;
      font-size: 12px;
      color: var(--text-muted);
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 8px;
    }
    .top-strip .brand-mark {
      display: flex;
      align-items: center;
      gap: 8px;
      color: var(--crimson);
      font-weight: 700;
      letter-spacing: 0.5px;
      text-transform: uppercase;
      font-size: 11.5px;
    }
    .font-switcher {
      display: flex;
      align-items: center;
      gap: 4px;
    }
    .font-switcher-label {
      font-size: 11px;
      color: var(--text-subtle);
      margin-right: 2px;
      font-weight: 600;
    }
    .font-btn {
      background: transparent;
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 3px 9px;
      font-size: 11px;
      font-weight: 600;
      color: var(--text-muted);
      cursor: pointer;
      font-family: var(--font-body);
      transition: all 0.15s ease;
    }
    .font-btn:hover {
      border-color: var(--border-dark);
      color: var(--text);
    }
    .font-btn.active {
      background: var(--crimson);
      color: #FFFFFF;
      border-color: var(--crimson);
    }

    .container {
      max-width: 820px;
      margin: 0 auto;
      padding: 0 20px;
    }

    /* EDITORIAL HERO SECTION */
    .hero-panel {
      margin-top: 24px;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius-lg);
      overflow: hidden;
      box-shadow: 0 4px 20px rgba(35, 25, 15, 0.04);
      display: flex;
      flex-direction: column;
    }
    @media (min-width: 640px) {
      .hero-panel {
        flex-direction: row;
      }
    }
    .hero-content {
      padding: 36px 32px;
      flex: 1.3;
      display: flex;
      flex-direction: column;
      justify-content: center;
    }
    .hero-image-wrap {
      flex: 0.9;
      min-height: 220px;
      position: relative;
      background: #330A12;
      overflow: hidden;
    }
    .hero-image-wrap img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      opacity: 0.85;
      display: block;
    }
    .hero-image-overlay {
      position: absolute;
      inset: 0;
      background: linear-gradient(135deg, rgba(85, 12, 23, 0.4) 0%, rgba(20, 3, 7, 0.6) 100%);
    }

    .kicker {
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 1.5px;
      color: var(--gold);
      margin-bottom: 8px;
    }
    h1.hero-title {
      font-family: var(--font-heading);
      font-size: 30px;
      font-weight: 800;
      line-height: 1.25;
      color: var(--text);
      letter-spacing: -0.5px;
      margin-bottom: 12px;
    }
    .hero-desc {
      font-size: 15px;
      color: var(--text-muted);
      line-height: 1.6;
      margin-bottom: 24px;
    }

    /* ACTION BUTTONS (Clean, authentic platform styling) */
    .sync-actions {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    @media (min-width: 480px) {
      .sync-actions {
        flex-direction: row;
      }
    }
    .btn-sync {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
      padding: 13px 20px;
      border-radius: var(--radius-md);
      font-size: 14.5px;
      font-weight: 600;
      text-decoration: none;
      transition: all 0.15s ease;
      cursor: pointer;
      border: 1px solid transparent;
      flex: 1;
    }
    .btn-apple {
      background: #111111;
      color: #FFFFFF;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
    }
    .btn-apple:hover {
      background: #222222;
    }
    .btn-google {
      background: #FFFFFF;
      color: #1F2937;
      border-color: var(--border-dark);
      box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
    }
    .btn-google:hover {
      background: #F9F9F9;
      border-color: #B0A799;
    }
    .btn-download-link {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      margin-top: 14px;
      font-size: 13px;
      color: var(--text-muted);
      text-decoration: none;
      font-weight: 500;
    }
    .btn-download-link:hover {
      color: var(--crimson);
      text-decoration: underline;
    }

    /* FEATURE BAR */
    .feature-strip {
      margin-top: 18px;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
      gap: 12px;
    }
    .feature-chip {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      padding: 12px 14px;
      display: flex;
      align-items: flex-start;
      gap: 10px;
    }
    .feature-chip svg {
      flex-shrink: 0;
      margin-top: 2px;
      color: var(--crimson);
    }
    .feature-chip-title {
      font-size: 13px;
      font-weight: 600;
      color: var(--text);
      line-height: 1.3;
    }
    .feature-chip-sub {
      font-size: 12px;
      color: var(--text-subtle);
      margin-top: 2px;
    }

    /* DIRECTORY TOOLBAR */
    .directory-toolbar {
      margin-top: 36px;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }
    @media (min-width: 600px) {
      .directory-toolbar {
        flex-direction: row;
        justify-content: space-between;
        align-items: center;
      }
    }
    .directory-heading {
      font-family: var(--font-heading);
      font-size: 22px;
      font-weight: 800;
      letter-spacing: -0.3px;
    }

    .filter-group {
      display: flex;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 30px;
      padding: 3px;
      gap: 2px;
      overflow-x: auto;
    }
    .filter-btn {
      background: transparent;
      border: none;
      padding: 6px 14px;
      font-size: 13px;
      font-weight: 600;
      color: var(--text-muted);
      border-radius: 20px;
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.15s ease;
    }
    .filter-btn.active {
      background: var(--crimson);
      color: #FFFFFF;
    }

    .search-box {
      position: relative;
      margin-top: 12px;
    }
    .search-box input {
      width: 100%;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      padding: 12px 16px 12px 42px;
      font-size: 14px;
      color: var(--text);
      outline: none;
      font-family: inherit;
      transition: border-color 0.15s;
    }
    .search-box input:focus {
      border-color: var(--crimson);
    }
    .search-box svg {
      position: absolute;
      left: 14px;
      top: 50%;
      transform: translateY(-50%);
      color: var(--text-subtle);
    }

    /* LITURGICAL DAY CARD */
    .events-stream {
      margin-top: 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .day-entry {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      display: flex;
      padding: 18px 20px;
      gap: 20px;
      transition: border-color 0.15s, box-shadow 0.15s;
    }
    .day-entry:hover {
      border-color: var(--border-dark);
      box-shadow: 0 4px 12px rgba(30, 20, 10, 0.03);
    }
    .day-entry.solemnity {
      border-left: 4px solid var(--crimson);
      background: linear-gradient(90deg, #FCF8F8 0%, #FFFFFF 25%);
    }
    .day-entry.feast {
      border-left: 4px solid var(--blue-tag);
    }
    .day-entry.memorial {
      border-left: 4px solid var(--green-tag);
    }

    /* Date column */
    .date-col {
      min-width: 58px;
      text-align: center;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: flex-start;
      border-right: 1px solid var(--border);
      padding-right: 16px;
    }
    .date-month {
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--text-subtle);
    }
    .date-num {
      font-family: var(--font-heading);
      font-size: 28px;
      font-weight: 800;
      line-height: 1;
      margin: 2px 0;
      color: var(--text);
    }
    .date-dow {
      font-size: 11.5px;
      color: var(--text-muted);
      font-weight: 500;
    }

    /* Content column */
    .content-col {
      flex: 1;
      min-width: 0;
    }
    .tags-row {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
      margin-bottom: 6px;
    }
    .tag {
      font-size: 10.5px;
      font-weight: 700;
      letter-spacing: 0.4px;
      text-transform: uppercase;
      padding: 2px 8px;
      border-radius: var(--radius-sm);
    }
    .tag-solemnity {
      background: var(--crimson-light);
      color: var(--crimson-dark);
      border: 1px solid #F0D5D8;
    }
    .tag-feast {
      background: var(--blue-bg);
      color: var(--blue-tag);
      border: 1px solid #D9E5F3;
    }
    .tag-memorial {
      background: var(--green-bg);
      color: var(--green-tag);
      border: 1px solid #D6EADF;
    }
    .tag-sunday {
      background: var(--gold-light);
      color: var(--gold);
      border: 1px solid var(--gold-border);
    }
    
    .vestment-dot {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      font-size: 11.5px;
      color: var(--text-muted);
      margin-left: 2px;
    }
    .color-circle {
      width: 9px;
      height: 9px;
      border-radius: 50%;
      display: inline-block;
      border: 1px solid rgba(0, 0, 0, 0.15);
    }
    .color-tr { background: #FFFFFF; }
    .color-dd { background: #D92534; }
    .color-xx { background: #1B8A44; }
    .color-tm { background: #7A35A8; }
    .color-hh { background: #E87299; }

    .entry-title {
      font-family: var(--font-heading);
      font-size: 16.5px;
      font-weight: 700;
      color: var(--text);
      line-height: 1.4;
      margin-bottom: 6px;
    }

    /* Readings section */
    .readings-panel {
      margin-top: 10px;
      background: #F7F5EE;
      border: 1px solid #EAE3D4;
      border-radius: 8px;
      padding: 9px 12px;
    }
    .readings-header {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.6px;
      color: var(--crimson);
      margin-bottom: 7px;
    }
    .readings-list {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }
    .reading-pill {
      background: #FFFFFF;
      border: 1px solid #DCD3C3;
      border-radius: 5px;
      padding: 3px 8px;
      font-size: 12px;
      font-weight: 600;
      color: #2D2820;
      box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
    }

    .notes-text {
      font-size: 12.5px;
      color: var(--text-muted);
      margin-top: 4px;
      margin-bottom: 4px;
      line-height: 1.4;
    }

    /* FOOTER */
    footer {
      margin-top: 60px;
      border-top: 1px solid var(--border);
      padding: 30px 20px;
      text-align: center;
      font-size: 13px;
      color: var(--text-muted);
    }
    footer a {
      color: var(--crimson);
      text-decoration: none;
      font-weight: 600;
    }

    /* ADMIN MODAL / DRAWER */
    .admin-trigger {
      background: none;
      border: none;
      color: var(--text-subtle);
      font-size: 12px;
      cursor: pointer;
      margin-top: 10px;
      text-decoration: underline;
    }
    .admin-panel {
      display: none;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      padding: 20px;
      margin-top: 20px;
      text-align: left;
    }
    .admin-textarea {
      width: 100%;
      height: 180px;
      font-family: monospace;
      font-size: 12.5px;
      padding: 12px;
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      margin: 10px 0;
    }
  </style>
</head>
<body>

  <!-- TOP MASTHEAD -->
  <div class="top-strip">
    <div class="brand-mark">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
        <path d="M11 2h2v7h7v2h-7v11h-2V11H4V9h7V2z"/>
      </svg>
      <span>Giáo Hội Công Giáo Việt Nam • Năm Phụng Vụ 2026</span>
    </div>
    <div class="font-switcher">
      <span class="font-switcher-label">Kiểu chữ:</span>
      <button class="font-btn active" id="fbtn-bevietnam" onclick="switchFont('bevietnam')">Hiện Đại</button>
      <button class="font-btn" id="fbtn-lora" onclick="switchFont('lora')">Trang Trọng (Lora)</button>
      <button class="font-btn" id="fbtn-playfair" onclick="switchFont('playfair')">Cổ Điển</button>
    </div>
  </div>

  <div class="container">

    <!-- EDITORIAL HERO PANEL -->
    <div class="hero-panel">
      <div class="hero-content">
        <div class="kicker">Đồng Bộ Lịch Điện Thoại</div>
        <h1 class="hero-title">Lịch Phụng Vụ & Lời Chúa</h1>
        <p class="hero-desc">
          Tự động cập nhật các ngày Lễ Trọng, Lễ Buộc và các bài đọc Lời Chúa trong Thánh lễ vào ứng dụng Lịch của iPhone và Android kèm thông báo nhắc lễ.
        </p>

        <!-- NATIVE 1-CLICK ACTION BUTTONS -->
        <div class="sync-actions">
          <a id="btnApple" href="#" class="btn-sync btn-apple">
            <svg width="17" height="17" viewBox="0 0 24 24" fill="currentColor">
              <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.81-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M15.97 6.37c.62-.75 1.04-1.8 0.92-2.85-.9.04-2 .6-2.65 1.35-.58.66-1.09 1.73-.95 2.76 1.01.08 2.05-.51 2.68-1.26z"/>
            </svg>
            <span>Thêm vào iPhone / iPad</span>
          </a>

          <a id="btnGoogle" href="#" target="_blank" class="btn-sync btn-google">
            <svg width="17" height="17" viewBox="0 0 24 24" fill="currentColor">
              <path d="M19 4h-1V2h-2v2H8V2H6v2H5c-1.11 0-1.99.9-1.99 2L3 20a2 2 0 0 0 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V9h14v11zM7 11h5v5H7z"/>
            </svg>
            <span>Google Calendar</span>
          </a>
        </div>

        <div>
          <a href="/calendar.ics" download="catholic_calendar_2026.ics" class="btn-download-link">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/>
            </svg>
            <span>Tải file chuẩn .ics (Nhập thủ công)</span>
          </a>
        </div>
      </div>

      <!-- SACRED ARTWORK WITH CLEAN VIGNETTE -->
      <div class="hero-image-wrap">
        <img src="/static/images/hero_banner.jpg" alt="Thánh Đường">
        <div class="hero-image-overlay"></div>
      </div>
    </div>

    <!-- SPECIFICATION CHIPS -->
    <div class="feature-strip">
      <div class="feature-chip">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
          <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
        </svg>
        <div>
          <div class="feature-chip-title">Nhắc Lễ Buộc & Lễ Trọng</div>
          <div class="feature-chip-sub">Báo trước lúc 20:00 tối hôm trước</div>
        </div>
      </div>

      <div class="feature-chip">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"></circle>
          <polyline points="12 6 12 12 16 14"></polyline>
        </svg>
        <div>
          <div class="feature-chip-title">Nhắc Sáng Ngày Lễ</div>
          <div class="feature-chip-sub">Chuông báo 07:00 ngày phụng vụ</div>
        </div>
      </div>

      <div class="feature-chip">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
          <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
        </svg>
        <div>
          <div class="feature-chip-title">Lời Chúa Trong Thánh Lễ</div>
          <div class="feature-chip-sub">Trích dẫn Cựu Ước, Đáp Ca, Tin Mừng</div>
        </div>
      </div>

      <div class="feature-chip">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="23 4 23 10 17 10"></polyline>
          <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
        </svg>
        <div>
          <div class="feature-chip-title">Tự Động Cập Nhật</div>
          <div class="feature-chip-sub">Đồng bộ qua chuẩn Webcal RFC 5545</div>
        </div>
      </div>
    </div>

    <!-- DIRECTORY SECTION -->
    <div class="directory-toolbar">
      <h2 class="directory-heading">Niên Lịch Phụng Vụ</h2>
      
      <div class="filter-group">
        <button class="filter-btn active" onclick="applyFilter('all')">Tất cả</button>
        <button class="filter-btn" onclick="applyFilter('solemnity')">Lễ Trọng & Buộc</button>
        <button class="filter-btn" onclick="applyFilter('10')">Tháng 10</button>
        <button class="filter-btn" onclick="applyFilter('11')">Tháng 11</button>
        <button class="filter-btn" onclick="applyFilter('12')">Tháng 12</button>
      </div>
    </div>

    <div class="search-box">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="11" cy="11" r="8"></circle>
        <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
      </svg>
      <input type="text" id="searchInput" placeholder="Tìm kiếm ngày lễ, tên Thánh, bài đọc Lời Chúa..." oninput="handleSearch()">
    </div>

    <div id="eventsList" class="events-stream">
      <!-- Injected via JavaScript -->
    </div>

    <!-- FOOTER -->
    <footer>
      <div>Lịch Phụng Vụ Công Giáo • Định dạng tiêu chuẩn iCalendar (RFC 5545)</div>
      <button class="admin-trigger" onclick="toggleAdmin()">Quản trị: Cập nhật dữ liệu phụng vụ mới</button>
      
      <div id="adminPanel" class="admin-panel">
        <h4 style="font-size: 14px; margin-bottom: 8px;">Cập nhật danh sách ngày lễ:</h4>
        <textarea id="adminInput" class="admin-textarea" placeholder="Dán văn bản ngày lễ mới..."></textarea>
        <button class="btn-sync btn-apple" style="padding: 8px 16px; font-size: 13px;" onclick="saveAdminData()">Lưu & Làm mới Lịch</button>
      </div>
    </footer>

  </div>

  <script>
    // Font switcher logic
    function switchFont(name) {
      document.body.className = 'font-' + name;
      document.querySelectorAll('.font-btn').forEach(b => b.classList.remove('active'));
      const activeBtn = document.getElementById('fbtn-' + name);
      if (activeBtn) activeBtn.classList.add('active');
      try { localStorage.setItem('preferred_font', name); } catch(e){}
    }
    const savedFont = (function() {
      try { return localStorage.getItem('preferred_font') || 'bevietnam'; } catch(e){ return 'bevietnam'; }
    })();
    switchFont(savedFont);

    const host = window.location.host;
    const protocol = window.location.protocol;
    
    // Webcal URL for iOS Safari (Native 1-tap subscription sheet)
    document.getElementById("btnApple").href = "webcal://" + host + "/calendar.ics";

    // Google Calendar render intent
    const fullIcs = protocol + "//" + host + "/calendar.ics";
    document.getElementById("btnGoogle").href = "https://calendar.google.com/calendar/render?cid=" + encodeURIComponent(fullIcs);

    let rawEvents = [];
    let currentFilter = 'all';

    async function fetchEvents() {
      try {
        const res = await fetch('/api/events');
        rawEvents = await res.json();
        render();
      } catch (err) {
        document.getElementById("eventsList").innerHTML = "<p style='text-align:center; padding: 30px;'>Không thể kết nối máy chủ.</p>";
      }
    }

    function applyFilter(f) {
      currentFilter = f;
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      event.target.classList.add('active');
      render();
    }

    function handleSearch() {
      render();
    }

    function getVestmentIndicator(colors) {
      if (!colors || colors.length === 0) return "";
      const map = {
        '(Tr)': { class: 'color-tr', label: 'Áo Trắng' },
        '(Đ)': { class: 'color-dd', label: 'Áo Đỏ' },
        '(X)': { class: 'color-xx', label: 'Áo Xanh' },
        '(Tm)': { class: 'color-tm', label: 'Áo Tím' },
        '(H)': { class: 'color-hh', label: 'Áo Hồng' }
      };
      return colors.map(c => {
        const item = map[c];
        if (!item) return "";
        return `<span class="vestment-dot"><span class="color-circle ${item.class}"></span>${item.label}</span>`;
      }).join(' ');
    }

    function render() {
      const container = document.getElementById("eventsList");
      const search = document.getElementById("searchInput").value.toLowerCase().trim();

      let filtered = rawEvents.filter(ev => {
        // Filter by category or month
        const parts = ev.date_str.split('/');
        const month = parts[1];

        if (currentFilter === 'solemnity') {
          if (!ev.is_solemnity) return false;
        } else if (currentFilter !== 'all') {
          if (month !== currentFilter && month !== '0' + currentFilter) return false;
        }

        // Search text
        if (search) {
          const readingsText = (ev.readings || []).join(' ');
          const haystack = (ev.summary + " " + (ev.clean_title || "") + " " + (ev.description || "") + " " + readingsText + " " + ev.date_str).toLowerCase();
          if (!haystack.includes(search)) return false;
        }

        return true;
      });

      if (filtered.length === 0) {
        container.innerHTML = "<div style='text-align: center; color: var(--text-subtle); padding: 40px;'>Không có ngày lễ nào phù hợp với bộ lọc.</div>";
        return;
      }

      container.innerHTML = filtered.map(ev => {
        const parts = ev.date_str.split('/');
        const dayNum = parts[0].padStart(2, '0');
        const monthNum = parts[1].padStart(2, '0');

        let cardClass = "day-entry";
        let tagHtml = "";

        if (ev.is_solemnity) {
          cardClass += " solemnity";
          const isObligation = (ev.rank && ev.rank.includes("BUỘC"));
          tagHtml = `<span class="tag tag-solemnity">${isObligation ? 'LỄ BUỘC' : 'LỄ TRỌNG'}</span>`;
        } else if (ev.is_feast) {
          cardClass += " feast";
          tagHtml = `<span class="tag tag-feast">LỄ KÍNH</span>`;
        } else if (ev.rank === 'Lễ nhớ' || ev.summary.includes('[Lễ nhớ]')) {
          cardClass += " memorial";
          tagHtml = `<span class="tag tag-memorial">LỄ NHỚ</span>`;
        } else if (ev.summary.includes('CHÚA NHẬT') || ev.is_sunday) {
          tagHtml = `<span class="tag tag-sunday">CHÚA NHẬT</span>`;
        }

        const vestmentHtml = getVestmentIndicator(ev.colors);

        // Clean title
        let cleanTitle = ev.clean_title || ev.summary
          .replace(/\[LỄ TRỌNG.*?\]/gi, '')
          .replace(/\[Lễ kính\]/gi, '')
          .replace(/\[Lễ nhớ\]/gi, '')
          .trim();

        // Render readings if present
        let readingsHtml = "";
        if (ev.readings && ev.readings.length > 0) {
          readingsHtml = `
            <div class="readings-panel">
              <div class="readings-header">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
                  <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
                  <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
                </svg>
                <span>Bài Đọc Lời Chúa Trong Thánh Lễ</span>
              </div>
              <div class="readings-list">
                ${ev.readings.map(r => `<span class="reading-pill">${r}</span>`).join('')}
              </div>
            </div>
          `;
        }

        // Render notes if present
        let notesHtml = "";
        if (ev.notes && ev.notes.length > 0) {
          notesHtml = `<div class="notes-text">${ev.notes.join(' • ')}</div>`;
        }

        return `
          <div class="${cardClass}">
            <div class="date-col">
              <span class="date-month">TH ${monthNum}</span>
              <span class="date-num">${dayNum}</span>
              <span class="date-dow">${ev.day_of_week}</span>
            </div>
            <div class="content-col">
              <div class="tags-row">
                ${tagHtml}
                ${vestmentHtml}
              </div>
              <div class="entry-title">${cleanTitle}</div>
              ${notesHtml}
              ${readingsHtml}
            </div>
          </div>
        `;
      }).join('');
    }

    function toggleAdmin() {
      const p = document.getElementById("adminPanel");
      p.style.display = (p.style.display === 'block') ? 'none' : 'block';
    }

    async function saveAdminData() {
      const text = document.getElementById("adminInput").value.trim();
      if (!text) return alert("Vui lòng nhập nội dung!");
      try {
        const res = await fetch('/api/update', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({content: text})
        });
        const data = await res.json();
        if (data.success) {
          alert("Đã cập nhật thành công!");
          fetchEvents();
          toggleAdmin();
        } else {
          alert("Lỗi: " + data.error);
        }
      } catch (e) {
        alert("Lỗi: " + e.message);
      }
    }

    fetchEvents();
  </script>
</body>
</html>
"""

async def handle_index(request):
    return web.Response(text=INDEX_HTML, content_type='text/html')

async def handle_ics(request):
    if not os.path.exists(ICS_FILE):
        reload_events()
    with open(ICS_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    
    headers = {
        "Content-Type": "text/calendar; charset=utf-8",
        "Content-Disposition": 'inline; filename="catholic_calendar.ics"',
        "Cache-Control": "no-cache, no-store, must-revalidate"
    }
    return web.Response(text=content, headers=headers)

async def handle_api_events(request):
    global current_events
    serialized = []
    for ev in current_events:
        serialized.append({
            "date_str": ev["date_str"],
            "day_of_week": ev["day_of_week"],
            "summary": ev["summary"],
            "clean_title": ev.get("clean_title", ""),
            "description": ev["description"],
            "rank": ev.get("rank"),
            "colors": ev.get("colors", []),
            "readings": ev.get("readings", []),
            "notes": ev.get("notes", []),
            "is_solemnity": ev.get("is_solemnity", False),
            "is_feast": ev.get("is_feast", False),
            "is_sunday": ev.get("is_sunday", False)
        })
    return web.json_response(serialized)

async def handle_api_update(request):
    global current_events
    try:
        data = await request.json()
        new_content = data.get("content", "")
        if not new_content:
            return web.json_response({"success": False, "error": "Nội dung trống."})

        with open(DATA_FILE, "w", encoding="utf-8") as f:
            f.write(new_content)

        current_events = reload_events()
        return web.json_response({"success": True, "total_events": len(current_events)})
    except Exception as e:
        return web.json_response({"success": False, "error": str(e)})

def make_app():
    app = web.Application()
    app.router.add_static('/static/', path='static', name='static')
    app.router.add_get('/', handle_index)
    app.router.add_get('/calendar.ics', handle_ics)
    app.router.add_get('/api/events', handle_api_events)
    app.router.add_post('/api/update', handle_api_update)
    return app

if __name__ == '__main__':
    print(f"Máy chủ Lịch Công Giáo đang chạy tại http://localhost:{PORT}")
    app = make_app()
    web.run_app(app, host='0.0.0.0', port=PORT)
