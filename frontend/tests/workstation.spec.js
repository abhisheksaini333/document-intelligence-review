import {test,expect} from '@playwright/test';
test('review queue renders and preserves document edits',async({page})=>{
 await page.goto(process.env.APP_URL||'http://127.0.0.1:4801');
 await expect(page.locator('h1')).toHaveText('Every document, accounted for.');
 await page.locator('.queue-item').first().click();
 await expect(page.locator('input[name="total"]')).toBeVisible();
 await page.locator('input[name="reviewer"]').fill('browser-reviewer');
 await page.locator('input[name="total"]').fill('110.00');
 await page.locator('button:has-text("Save corrections")').click();
 await expect(page.locator('[role="status"]')).toContainText('Corrections saved');
 await page.locator('button:has-text("Approve document")').click();
 await expect(page.locator('[role="status"]')).toContainText('Document approved');
 await page.reload();
 await page.locator('.queue-item').first().click();
 await expect(page.locator('input[name="total"]')).toHaveValue('110.00');
 const feedback=await page.evaluate(async()=>fetch('/api/feedback').then(r=>r.json()));
 expect(feedback.length).toBeGreaterThan(0);expect(feedback[0].fields.total).toBe('110.00');
 if(process.env.DOCREVIEW_SCREENSHOT){await page.locator('input[name="total"]').focus();await page.screenshot({path:process.env.DOCREVIEW_SCREENSHOT,fullPage:true});}
});
