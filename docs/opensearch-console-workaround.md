# OpenSearch Console IAM ARN Workaround

**Issue**: Console IAM ARN field resets to blank when editing.

**Quick Fix**: The domain configuration shows `InternalUserDatabaseEnabled: false`, which suggests IAM might already be configured. Let's test if it's working first.

---

## Immediate Action: Test Current Configuration

Run this to test if IAM authentication is already working:

```bash
./scripts/test-opensearch-iam-access.sh
```

**If test passes**: IAM is configured! You just need to set up role mappings in OpenSearch Dashboards.

**If test fails**: We need to configure IAM authentication (console issue or configuration needed).

---

## Console Workarounds

### Workaround 1: Type Instead of Paste

The console might have issues with paste. Try:

1. Clear the field completely
2. **Type the ARN manually** (don't paste)
3. Verify it stays in the field
4. Save immediately

### Workaround 2: Use Browser Developer Tools

1. **Open Developer Tools** (F12)
2. **Go to Elements/Inspector tab**
3. **Find the IAM ARN input field**
4. **Manually set the value** via JavaScript:
   ```javascript
   document.querySelector('input[aria-label*="IAM ARN"]').value = 'arn:aws:iam::720119760662:role/ComputeStack-DocumentProcessorRole12EFF6D7-bd7GiR8pj4uB'
   ```
5. **Then click Save**

### Workaround 3: Check if Already Configured

The domain shows `InternalUserDatabaseEnabled: false`, which **usually means IAM is configured**. 

**Test it**:
```bash
./scripts/test-opensearch-iam-access.sh
```

If it works, the console is just not displaying the value correctly - the configuration is fine!

---

## Alternative: Skip Master User Change, Use Role Mappings

If changing the master user keeps failing, you can:

1. **Keep master user as username/password** (for Dashboards access)
2. **Configure role mappings** in OpenSearch Dashboards to allow Lambda IAM roles
3. **Lambda still uses IAM authentication** - it will work!

This approach is actually common in production - master user for admin access, role mappings for service access.

---

## Next Steps

1. **Test current configuration**: `./scripts/test-opensearch-iam-access.sh`
2. **If test passes**: Configure role mappings (see `docs/iam-authentication-migration.md`)
3. **If test fails**: Try console workarounds or contact AWS Support

The console UI issue might be a red herring - let's verify if IAM is already working first!

