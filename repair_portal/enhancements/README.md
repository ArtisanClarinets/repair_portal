# Enhancements Module

## 📌 Overview
Handles customer-requested upgrades and enhancements to clarinets during the service process. Tracks both the requests and the upgrade options available.

---

## 📄 Doctypes
- **Customer Upgrade Request**
  - Links to Customer and Instrument
  - Logged in Instrument Tracker
  - Triggers workflow if enhancement is approved

- **Upgrade Option**
  - Defines predefined upgrade services
  - Linkable from Customer Upgrade Requests

---

## 👥 Roles
- **Service Manager**: Full access
- **Repair Administrator**: View only

---

## 🔁 Flow
1. Technician or Reception logs a request
2. Manager reviews, links to Upgrade Option
3. Logged to Tracker upon approval
