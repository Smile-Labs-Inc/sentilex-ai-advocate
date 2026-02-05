import { PayPalButtons, PayPalScriptProvider } from "@paypal/react-paypal-js";
import { API_CONFIG } from "../../../config";
import { useState } from "preact/hooks";

interface PayPalPaymentProps {
  amount: string; // e.g., "29.99"
  planName: string; // e.g., "Pro Plan"
  onSuccess: (details: any) => void;
  onError?: (error: any) => void;
}

export function PayPalPayment({
  amount,
  planName,
  onSuccess,
  onError,
}: PayPalPaymentProps) {
  const [isPaying, setIsPaying] = useState(false);

  const initialOptions = {
    clientId: API_CONFIG.PAYPAL_CLIENT_ID,
    currency: "USD",
    intent: "capture",
  };

  return (
    <div className="w-full">
      <PayPalScriptProvider options={initialOptions}>
        <PayPalButtons
          disabled={isPaying}
          style={{
            layout: "vertical",
            color: "gold",
            shape: "rect",
            label: "paypal",
          }}
          createOrder={(data, actions) => {
            setIsPaying(true);
            return actions.order.create({
              purchase_units: [
                {
                  description: planName,
                  amount: {
                    value: amount,
                  },
                },
              ],
            });
          }}
          onApprove={async (data, actions) => {
            try {
              const details = await actions.order!.capture();
              console.log("Payment successful:", details);
              setIsPaying(false);
              onSuccess(details);
            } catch (error) {
              console.error("Payment capture error:", error);
              setIsPaying(false);
              onError?.(error);
            }
          }}
          onError={(err) => {
            console.error("PayPal error:", err);
            setIsPaying(false);
            onError?.(err);
          }}
          onCancel={() => {
            console.log("Payment cancelled");
            setIsPaying(false);
          }}
        />
      </PayPalScriptProvider>
    </div>
  );
}
