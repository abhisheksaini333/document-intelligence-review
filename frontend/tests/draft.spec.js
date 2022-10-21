import {test,expect} from '@playwright/test';
test('unsaved corrections survive queue navigation attempts',async({page})=>{
 await page.goto('http://127.0.0.1:4801');await page.locator('.queue-item').first().click();await page.locator('input[name="total"]').fill('999.00');
 await page.locator('.queue-item').nth(1).click();
 await expect(page.locator('[role="alert"]')).toContainText('Save or discard');
 await expect(page.locator('input[name="total"]')).toHaveValue('999.00');
 await page.locator('button:has-text("Discard changes")').click();await page.locator('.queue-item').nth(1).click();
 await expect(page.locator('.queue-item.selected')).toContainText('second.png');
});
