import {test,expect} from '@playwright/test';
test('a stale browser cannot replace another reviewers saved correction',async({browser})=>{
 const context=await browser.newContext();const first=await context.newPage();const second=await context.newPage();const url=process.env.APP_URL||'http://127.0.0.1:4801';
 await first.goto(url);await second.goto(url);await first.locator('.queue-item').first().click();await second.locator('.queue-item').first().click();
 await first.locator('input[name="reviewer"]').fill('first-reviewer');await first.locator('input[name="number"]').fill('INV-FIRST');await first.locator('button:has-text("Save corrections")').click();await expect(first.locator('[role="status"]')).toContainText('Corrections saved');
 await second.locator('input[name="reviewer"]').fill('second-reviewer');await second.locator('input[name="number"]').fill('INV-STALE');await second.locator('button:has-text("Save corrections")').click();await expect(second.locator('[role="alert"]')).toContainText('Someone changed');await expect(second.locator('input[name="number"]')).toHaveValue('INV-STALE');
 await second.locator('button:has-text("Reload latest version")').click();await expect(second.locator('input[name="number"]')).toHaveValue('INV-FIRST');await context.close();
});
