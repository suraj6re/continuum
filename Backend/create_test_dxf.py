import ezdxf

# Create a new DXF document
doc = ezdxf.new('R2010')
msp = doc.modelspace()

# Add sheet border (rectangle)
msp.add_line((0, 0), (297, 0))      # Bottom
msp.add_line((297, 0), (297, 210))  # Right
msp.add_line((297, 210), (0, 210))  # Top
msp.add_line((0, 210), (0, 0))      # Left

# Add some internal geometry
msp.add_line((50, 50), (150, 50))
msp.add_line((150, 50), (150, 100))
msp.add_line((150, 100), (50, 100))
msp.add_line((50, 100), (50, 50))

# Add text entities (for clustering)
msp.add_text("Title Block", dxfattribs={'height': 5}).set_placement((10, 10))
msp.add_text("Drawing No: 001", dxfattribs={'height': 3}).set_placement((10, 20))
msp.add_text("Scale: 1:100", dxfattribs={'height': 3}).set_placement((10, 30))
msp.add_text("Date: 2024", dxfattribs={'height': 3}).set_placement((10, 40))
msp.add_text("Room A", dxfattribs={'height': 4}).set_placement((100, 75))
msp.add_text("3.5m x 2.5m", dxfattribs={'height': 2.5}).set_placement((95, 65))

# Save
doc.saveas('../imputs/1.dxf')
print("Test DXF created at: ../imputs/1.dxf")
