import {test,expect} from '@playwright/test';
test('field focus highlights the exact source evidence',async({page})=>{
 await page.goto('http://127.0.0.1:4801');await page.locator('.queue-item').first().click();
 await page.locator('input[name="total"]').focus();
 await expect(page.locator('[data-evidence="total"]')).toBeVisible();
 await expect(page.locator('[aria-label="Source page"]')).toHaveValue('1');
});
