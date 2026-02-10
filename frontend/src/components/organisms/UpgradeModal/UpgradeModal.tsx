import { useState } from "preact/hooks";
import { PayPalPayment } from "../PayPalPayment/PayPalPayment";
import { Icon } from "../../atoms/Icon/Icon";
import { Button } from "../../atoms/Button/Button";

interface UpgradeModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function UpgradeModal({ isOpen, onClose }: UpgradeModalProps) {
  const [paymentSuccess, setPaymentSuccess] = useState(false);
  const [paymentError, setPaymentError] = useState<string | null>(null);

  const handlePaymentSuccess = async (details: any) => {
    
    setPaymentSuccess(true);

    // TODO: Send payment details to your backend to upgrade the user
    // Example:
    // await fetch(`${API_CONFIG.BASE_URL}/payments/upgrade`, {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify({
    //     orderId: details.id,
    //     status: details.status
    //   })
    // });

    // Close modal after 2 seconds
    setTimeout(() => {
      onClose();
      window.location.reload(); // Refresh to show updated plan
    }, 2000);
  };

  const handlePaymentError = (error: any) => {
    
    setPaymentError("Payment failed. Please try again.");
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="bg-card rounded-xl shadow-2xl max-w-lg w-full max-h-[90vh] overflow-y-auto border border-border">
        {/* Header */}
        <div className="p-6 border-b border-border">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Icon name="Crown" size="md" className="text-yellow-500" />
              <h2 className="text-xl font-bold text-foreground">
                Upgrade to Pro
              </h2>
            </div>
            <button
              onClick={onClose}
              className="text-muted-foreground hover:text-foreground transition-colors"
            >
              <Icon name="X" size="sm" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          {paymentSuccess ? (
            <div className="text-center py-8">
              <div className="text-green-500 mb-4">
                <Icon name="CheckCircle2" size="xl" className="mx-auto" />
              </div>
              <h3 className="text-lg font-semibold text-foreground mb-2">
                Payment Successful!
              </h3>
              <p className="text-muted-foreground text-sm">
                Your account has been upgraded to Pro. Redirecting...
              </p>
            </div>
          ) : (
            <>
              {/* Plan Details */}
              <div className="bg-gradient-to-br from-secondary/50 to-background border border-border rounded-lg p-6 mb-6">
                <div className="text-center mb-4">
                  <div className="text-4xl font-bold text-foreground mb-2">
                    $29.99
                    <span className="text-lg text-muted-foreground">
                      /month
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground">Pro Plan</p>
                </div>

                <div className="space-y-3">
                  <div className="flex items-start gap-2">
                    <Icon
                      name="Check"
                      size="sm"
                      className="text-green-500 mt-0.5"
                    />
                    <span className="text-sm text-foreground">
                      Priority AI support
                    </span>
                  </div>
                  <div className="flex items-start gap-2">
                    <Icon
                      name="Check"
                      size="sm"
                      className="text-green-500 mt-0.5"
                    />
                    <span className="text-sm text-foreground">
                      Unlimited case storage
                    </span>
                  </div>
                  <div className="flex items-start gap-2">
                    <Icon
                      name="Check"
                      size="sm"
                      className="text-green-500 mt-0.5"
                    />
                    <span className="text-sm text-foreground">
                      Advanced analytics
                    </span>
                  </div>
                  <div className="flex items-start gap-2">
                    <Icon
                      name="Check"
                      size="sm"
                      className="text-green-500 mt-0.5"
                    />
                    <span className="text-sm text-foreground">
                      24/7 legal consultation
                    </span>
                  </div>
                  <div className="flex items-start gap-2">
                    <Icon
                      name="Check"
                      size="sm"
                      className="text-green-500 mt-0.5"
                    />
                    <span className="text-sm text-foreground">
                      Priority lawyer matching
                    </span>
                  </div>
                </div>
              </div>

              {/* Error Message */}
              {paymentError && (
                <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4 mb-4">
                  <p className="text-sm text-red-500">{paymentError}</p>
                </div>
              )}

              {/* PayPal Buttons */}
              <div className="mb-4">
                <PayPalPayment
                  amount="29.99"
                  planName="SentiLex Pro Plan"
                  onSuccess={handlePaymentSuccess}
                  onError={handlePaymentError}
                />
              </div>

              <p className="text-xs text-center text-muted-foreground">
                Secure payment processed by PayPal. Cancel anytime.
              </p>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
