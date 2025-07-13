-- Migration: Add items_not_sent counter to orders table
-- Created: 2025-07-13
-- Description: Adds items_not_sent column to track items marked as not sent

ALTER TABLE orders ADD COLUMN items_not_sent INTEGER DEFAULT 0 NOT NULL;

-- Update existing orders to calculate not_sent items count
UPDATE orders 
SET items_not_sent = (
    SELECT COUNT(*) 
    FROM order_items 
    WHERE order_items.order_id = orders.id 
    AND order_items.not_sent = 1
);