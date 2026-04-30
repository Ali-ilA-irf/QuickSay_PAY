import os
import tempfile
import webbrowser
from datetime import datetime

def export_transactions_html(customer_name, account_number, transactions, save_path=None):
    """
    Generates a beautiful HTML statement for transactions and opens it in the default browser.
    The user can then print it to PDF.
    transactions should be a list of dicts/lists with keys: Date, Type, Amount, Account, Beneficiary.
    """
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Account Statement - {account_number}</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Inter:wght@400;600&display=swap');
            
            body {{
                font-family: 'Inter', sans-serif;
                background-color: #F9FAFB;
                color: #111827;
                margin: 0;
                padding: 40px;
            }}
            .container {{
                max-width: 800px;
                margin: 0 auto;
                background-color: #FFFFFF;
                padding: 40px;
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            }}
            .header {{
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                border-bottom: 2px solid #E5E7EB;
                padding-bottom: 20px;
                margin-bottom: 30px;
            }}
            .brand h1 {{
                font-family: 'Playfair Display', serif;
                color: #0D1B2A;
                margin: 0;
                font-size: 28px;
            }}
            .brand p {{
                color: #E8A020;
                margin: 5px 0 0 0;
                font-style: italic;
                font-family: 'Playfair Display', serif;
            }}
            .statement-info {{
                text-align: right;
            }}
            .statement-info h2 {{
                margin: 0;
                color: #374151;
                font-size: 20px;
            }}
            .statement-info p {{
                margin: 5px 0 0 0;
                color: #6B7280;
                font-size: 14px;
            }}
            .customer-info {{
                margin-bottom: 30px;
            }}
            .customer-info strong {{
                color: #111827;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            th, td {{
                padding: 12px 15px;
                text-align: left;
                border-bottom: 1px solid #E5E7EB;
            }}
            th {{
                background-color: #F3F4F6;
                color: #374151;
                font-weight: 600;
                font-size: 13px;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }}
            td {{
                font-size: 14px;
            }}
            .amount-pos {{
                color: #059669;
                font-weight: 600;
            }}
            .amount-neg {{
                color: #DC2626;
                font-weight: 600;
            }}
            .footer {{
                margin-top: 50px;
                text-align: center;
                color: #9CA3AF;
                font-size: 12px;
                border-top: 1px solid #E5E7EB;
                padding-top: 20px;
            }}
            
            @media print {{
                body {{ background-color: white; padding: 0; }}
                .container {{ box-shadow: none; max-width: 100%; }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="brand">
                    <h1>QuickSay Pay</h1>
                    <p>Apke Dill Mein Hmara Account</p>
                </div>
                <div class="statement-info">
                    <h2>Account Statement</h2>
                    <p>Generated: {datetime.now().strftime('%d %B %Y, %I:%M %p')}</p>
                </div>
            </div>
            
            <div class="customer-info">
                <p><strong>Customer Name:</strong> {customer_name}</p>
                <p><strong>Account Number:</strong> {account_number}</p>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Description</th>
                        <th>Reference</th>
                        <th style="text-align: right;">Amount (PKR)</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for t in transactions:
        # Expecting either list [date, type, amount, acc, ref] or dict
        if isinstance(t, list):
            date, ttype, amt, acc, ref = t[:5]
        else:
            date = t.get("TXN_DATE", "")
            ttype = t.get("TRANSACTION_TYPE", "")
            amt = f"PKR {float(t.get('TRANSACTION_AMOUNT') or 0):,.2f}"
            acc = t.get("ACCOUNT_NUMBER", "")
            ref = t.get("RECEIVING_ACCOUNT", "")
            
        amt_class = "amount-pos" if "DEPOSIT" in ttype.upper() or "RECEIVED" in ttype.upper() else "amount-neg"
        prefix = "+" if amt_class == "amount-pos" else "-"
        amt_display = str(amt).replace("PKR", "").strip()
        
        html_content += f"""
                    <tr>
                        <td>{date}</td>
                        <td>{ttype}</td>
                        <td>{ref if ref else '-'}</td>
                        <td style="text-align: right;" class="{amt_class}">{prefix} {amt_display}</td>
                    </tr>
        """
        
    html_content += """
                </tbody>
            </table>
            
            <div class="footer">
                <p>This is a computer generated statement and does not require a physical signature.</p>
                <p>&copy; 2026 QuickSay Pay. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    if not save_path:
        # Create temporary file
        fd, save_path = tempfile.mkstemp(suffix=".html", prefix="quicksay_statement_")
        os.close(fd)
        
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    webbrowser.open(f"file://{os.path.abspath(save_path)}")
    return save_path
