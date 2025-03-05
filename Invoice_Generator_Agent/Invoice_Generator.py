import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
import os

class InvoiceGenerator:
    def __init__(self):
        """Initialize the invoice generator with user input."""
        self.invoice_data = {}
        self.invoice_df = None  

    def get_user_input(self):
        """Collects invoice details from user via terminal."""
        print("\n=== Invoice Generator AI Agent ===\n")
        
        # Basic business details
        self.invoice_data["Business Name"] = input("Enter your Business Name: ")
        self.invoice_data["Business Description"] = input("Enter Business Description: ")
        self.invoice_data["Logo"] = input("Enter Logo file path (leave blank if none): ")
        self.invoice_data["Your Business Address"] = input("Enter your Business Address: ")
        
        # Customer details
        self.invoice_data["Customer Name"] = input("Enter Customer Name: ")
        self.invoice_data["Name for Billing"] = input("Enter Name for Billing: ")
        self.invoice_data["Payment Due Date"] = input("Enter Payment Due Date (YYYY-MM-DD): ")
        
        # Bank details
        self.invoice_data["Bank Details"] = input("Enter Bank Details: ")

        # Invoice Items - Dynamic Input
        print("\nEnter Invoice Items (Type 'done' when finished):")
        items = []
        while True:
            item_name = input("Enter Item Name (or type 'done' to finish): ")
            if item_name.lower() == 'done':
                break
            quantity = int(input(f"Enter Quantity for {item_name}: "))
            price = float(input(f"Enter Price for {item_name}: "))
            items.append({"Item": item_name, "Quantity": quantity, "Price": price})
        
        self.invoice_data["Invoice Items"] = items

    def prepare_invoice_data(self):
        """Converts user input into a DataFrame and ensures 'Total' column is calculated."""
        self.invoice_df = pd.DataFrame(self.invoice_data['Invoice Items'])
        
        if 'Quantity' in self.invoice_df.columns and 'Price' in self.invoice_df.columns:
            self.invoice_df['Total'] = self.invoice_df['Quantity'] * self.invoice_df['Price']
        else:
            raise KeyError("Missing required columns: 'Quantity' or 'Price' in invoice data.")

    def generate_pdf(self, output_filename="invoice.pdf"):
        """Generates a PDF invoice from the structured data with a professional table layout."""
        if self.invoice_df is None:
            raise ValueError("Invoice data not prepared. Run prepare_invoice_data() first.")

        c = canvas.Canvas(output_filename, pagesize=letter)
        width, height = letter

        # Business Name & Logo
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, self.invoice_data['Business Name'])

        if self.invoice_data.get('Logo'):
            logo_path = self.invoice_data['Logo']
            if os.path.exists(logo_path):
                c.drawImage(logo_path, 400, height - 80, width=150, height=50)

        # Business & Customer Details
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 80, f"Business Address: {self.invoice_data['Your Business Address']}")
        c.drawString(50, height - 100, f"Customer Name: {self.invoice_data['Customer Name']}")
        c.drawString(50, height - 120, f"Billing Contact: {self.invoice_data['Name for Billing']}")
        c.drawString(50, height - 140, f"Payment Due: {self.invoice_data['Payment Due Date']}")

        # Table Header
        y_position = height - 180

        # Define table data (including headers)
        table_data = [["Item", "Quantity", "Price", "Total"]]
        for _, row in self.invoice_df.iterrows():
            table_data.append([
                row.get('Item', 'N/A'),
                str(row.get('Quantity', 0)),
                f"${row.get('Price', 0.00):.2f}",
                f"${row.get('Total', 0.00):.2f}"
            ])
        
        # Define Table Styling
        table = Table(table_data, colWidths=[200, 100, 100, 100])
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Header background
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Header text color
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Align all cells to center
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Bold header
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),  # Padding for header
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),  # Background for body
            ('GRID', (0, 0), (-1, -1), 1, colors.black)  # Grid lines for table
        ])
        table.setStyle(style)

        # Draw Table on PDF
        table.wrapOn(c, width, height)
        table.drawOn(c, 50, y_position - (len(table_data) * 20))

        # Calculate Grand Total
        grand_total = self.invoice_df['Total'].sum()

        # Grand Total Display
        c.setFont("Helvetica-Bold", 12)
        c.drawString(400, y_position - (len(table_data) * 20) - 30, "Grand Total:")
        c.drawString(500, y_position - (len(table_data) * 20) - 30, f"${grand_total:.2f}")

        # Bank Details
        c.setFont("Helvetica", 10)
        c.drawString(50, y_position - (len(table_data) * 20) - 80, f"Bank Details: {self.invoice_data['Bank Details']}")

        # Save PDF
        c.save()
        print(f"\n✅ Invoice PDF Generated: {output_filename}")

# Run the Invoice Generator
invoice_generator = InvoiceGenerator()
invoice_generator.get_user_input()
invoice_generator.prepare_invoice_data()
invoice_generator.generate_pdf("generated_invoice.pdf")
